from url_generator.utils import *
from DreamTV_world import tasks
from url_generator.models import UrlGenerator, StopDomain, SearchUrlStack


def youtube_links_in_source(source, key=''):
    res = False
    if 'youtube.com/watch?v=%s' % key in source \
            or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
            or ('youtube.com/player_api' in source and "videoId: '%s'" % key in source):
        res = True

    return res

def url_is_valid(url_obj):
    error = _check_if_url_in_stop_domain_list_or_our_base(url_obj)
    if not error:
        source_result, error = tasks.test_the_url(url_obj.url)

        if error or not source_result:
            item = SearchUrlStack.objects.get(url=url_obj.url)
            item.attempt +=1
            item.save()
            if item.attempt > 3:
                SearchUrlStack.objects.filter(domain=url_obj.domain).delete()
                error = 'URL IS NOT WORKING for 3 attemprs - URL DELETED - %s' % url_obj.url

    return error

def find_key_in_url(url, key):
    url_obj = UrlConstructor(url)
    res, error = _find_key_direct(url_obj, key)

    if not res and not error and len(url_obj.separate_11_list) > 0:
        res, error = _find_key_by_separate_11(url_obj, key)

    if not res and not error and len(_find_x_from_list_in_url(url_obj.url)) > 0:
        res, error = _find_key_by_v_args_in_url(url_obj, key)

    if not res:
        error = 'ERROR: key not found in url %s' % url
  
    return res, error

def find_anc_in_url(tmp_res, slug, slug_uni):
    url_obj = UrlConstructor(tmp_res)
    check_url = tmp_res
    need_manual_check = False

    res, error = _find_anc_direct(url_obj, slug, slug_uni)

    if not res and not error:
        res, need_manual_check, error = _find_anc_in_separate_long_list(url_obj)

    return res, need_manual_check, error

def add_url_to_stop_domain_list(url):
    error = 'DO NOT HAVE A KEY -- HAVE NO IDEA WHAT TO DO -- URL ADDED TO StopDomain'

    StopDomain.objects.create(domain=get_domain_name(url), url=url[0:510], reason=error)
    SearchUrlStack.objects.filter(domain=get_domain_name(url)).delete()

    return error

def _check_if_url_in_stop_domain_list_or_our_base(url_obj):
    error = None

    if len(StopDomain.objects.filter(domain=url_obj.domain)) != 0 or url_obj.domain in UrlGenerator.domains.domeins_all():
        error = 'This url domain - %s is in StopDomain or it is alredy in our base. URL DECLINED' % url_obj.domain
        SearchUrlStack.objects.filter(url=url_obj.url).delete()

    return error

def _find_key_direct(url_obj, key):
    keys = _get_key_variations_dic(key)
    res = None
    error = None

    for i in keys.keys():
        if url_obj.url.find(i) != -1:
            check_url = url_obj.url.replace(i, keys[i])
            if tasks.task_check_this_url(check_url):
                res = check_url
            else:
                error = 'Have exact key - %s match in url - %s, but url does not work' % (key, url_obj.url)

    return res, error

def _find_anc_direct(url_obj, slug, slug_uni):
    slug = slug or 'xxx-xxxx-xxxxx-xxxxxxx'
    slug_uni = slug_uni or 'xxx-xxxx-xxxxx-xxxxxxx'

    res, error = _find_anc_direct_anc_checker(url_obj, slug)

    if not res and not error:
        res, error = _find_anc_direct_anc_checker(url_obj, slug_uni)

    return res, error

def _find_anc_direct_anc_checker(url_obj, slug):
    res = None
    error = None

    if url_obj.url.lower().find(slug) != -1:
        fragment = url_obj.url[url_obj.url.lower().find(slug):url_obj.url.lower().find(slug)+len(slug)]
        check_url = url_obj.url.replace(fragment, '!anc!')
        if tasks.task_check_this_url(check_url):
            res = check_url
        else:
            error = 'Have exact slug match in url %s, but url does not work with other !anc!' % slug

    return res, error

def _find_anc_in_separate_long_list(url_obj):
    res = None
    error = None
    need_manual_check = False

    if len(url_obj.separate_long_list) != 0:
        for part in url_obj.separate_long_list:
            in_this_part = _find_key_marker_in_str(part)
            if not in_this_part:
                check = _lets_check(url_obj, part, '!anc!')
                if check:
                    res = check
                    break
            else:
                check = _lets_check(url_obj, part, '!anc!-%s' % in_this_part)
                if check:
                    res = check
                    break

                check = _lets_check(url_obj, part, '%s-!anc!' % in_this_part)
                if check:
                    res = check
                    break
        if not res:
            need_manual_check = True
            res = url_obj.url

    return res, need_manual_check, error

def _lets_check(url_obj, fragment, var):
    res = None
    check_url = url_obj.url.replace(fragment, var)
    if tasks.task_check_this_url(check_url):
        res = check_url
    return res

def _find_key_marker_in_str(string):
    list = ['!key!', '!-key!', '!key|lowercase!']
    res = None
    for item in list:
        if string.find(item) != -1:
            res = item
            break
    return res

def _find_key_by_separate_11(url_obj, key):
    key_vars = ['!key!', '!key!' '!key!']
    res = None
    error = None

    for str_11 in url_obj.separate_11_list:
        for kv in key_vars:
            if not res and tasks.task_check_this_url(str(url_obj.url).replace(str_11, kv)):
                res = url_obj.url.replace(str_11, kv)
                break

    return res, error

def _find_key_by_v_args_in_url(url_obj, key):
    url = url_obj.url
    res = None
    error = None

    for item in _find_x_from_list_in_url(url):
        test_arg = url[url.find(item)+len(item): url.find(item)+len(item)+11]

        if not res and tasks.task_check_this_url(url_obj.url.replace(test_arg, '!key!')):
            res = url_obj.url.replace(test_arg, '!key!')

        elif not res and tasks.task_check_this_url(url_obj.url.replace(test_arg, '!-key!')):
            res = url_obj.url.replace(test_arg, '!-key!')

        elif not res and tasks.task_check_this_url(url_obj.url.replace(test_arg, '!key|lowercase!')):
            res = url_obj.url.replace(test_arg, '!key|lowercase!')

    return res, error

def _get_key_variations_dic(key):
    return {key: '!key!', ''.join(reversed(key)): '!-key!', key.lower():'!key|lowercase!'}

def _find_x_from_list_in_url(url):
    v_args = ['?v=', 'id=', 'video=', 'video-', '?q=', 'download-', 'download=']
    res = []

    for item in v_args:
        if url.find(item) != -1:
            res.append(item)

    return res

    # v_separs = ['detail', 'video', 'watch', 'show', 'download', 'download-music', 'music', 'videodek', 'embed', 'embeded', 'mobile', 'code',
    #             'view', 'baixar', 'play', 'movies', 'search', 'tv', 'getvideo', 'get', 'mp3', 'src', 'lagu', 'related', 'video-dl', 'key',
    #             '!key!', '!-key!', '!key|lowercase!', '!anc!']





