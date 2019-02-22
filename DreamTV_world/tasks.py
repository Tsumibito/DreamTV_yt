from DreamTV_world.celery import app
from url_generator.utils import *
from selenium import webdriver
from url_generator.models import UrlGenerator, StopDomain, SearchUrlStack, SearchStack
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from django.utils.text import slugify
from unidecode import unidecode
from random import randint
import sys
#from celery.utils.log import get_task_logger
import urllib

import time
# celery worker -A DreamTV_world --loglevel=debug --concurrency=4
# celery -f purge
# redis-cli flushall

#logger = get_task_logger(__name__)

@app.task(default_retry_delay=60, max_retries=3, soft_time_limit=120)
def task_check_UrlGenerator_url(url_name):
    key = '4pCD17L_bRE'
    desc = 'Истоки философского мышления 4'
    url_instance = UrlGenerator.objects.get(url=url_name)

    url = insert_data_in_url(str(url_instance.url), key)
    res = False

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (get_useraget())
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)

    browser.get(url)
    source = get_source_with_iframes(browser)
    if browser.current_url == url and desc.lower() in source.lower() and 'youtube.com/watch?v=%s' % key in source \
            or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
            or ('youtube.com/player_api' in source and "videoId: '%s'" % key in source):
        res = True
    else:
        time.sleep(7)
        source = get_source_with_iframes(browser)
        if browser.current_url == url and desc.lower() in source.lower() and 'youtube.com/watch?v=%s' % key in source \
                or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
                or ('youtube.com/player_api' in source and "videoId: '%s'" % key in source):
            res = True
        elif browser.current_url != url and url.replace(get_http_and_domain(url), get_http_and_domain(browser.current_url)) == browser.current_url \
                and desc.lower() in source.lower() and 'youtube.com/watch?v=%s' % key in source \
                or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
                or ('youtube.com/player_api' in source and "videoId: '%s'" % key in source):
            url_instance.url = str(url_instance.url).replace(get_http_and_domain(url), get_http_and_domain(browser.current_url))
            url_instance.save()
            res = True
        elif browser.current_url != url and desc.lower() in source.lower() and 'youtube.com/watch?v=%s' % key in source \
                or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
                or ('youtube.com/player_api' in source and "videoId: '%s'" % key in source):
            url_instance.need_review = True
            url_instance.save()

    if res == True:
        activate_url(url_instance)
    else:
        print(url_instance, 'URL DEActivated')
        deactivate_url(url_instance)

    browser.quit()
    return res

@app.task(default_retry_delay=60, max_retries=3, soft_time_limit=120)
def task_check_this_url(url_template):

    key = '4pCD17L_bRE'
    desc = 'Истоки философского мышления 4'

    url = insert_data_in_url(str(url_template), key)
    res = False

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (get_useraget())
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)
    try:
        browser.get(url)
        source = get_source_with_iframes(browser)
        if browser.current_url == url and desc.lower() in source.lower() and 'youtube.com/watch?v=%s' % key in source \
                or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
                or ('youtube.com/player_api' in source and "videoId: '%s'" % key in source):
            res = True
        else:
            time.sleep(5)
            source = get_source_with_iframes(browser)
            if browser.current_url == url and desc.lower() in source.lower() and 'youtube.com/watch?v=%s' % key in source \
                    or 'youtube-nocookie.com/embed/%s' % key in source or 'youtube.com/embed/%s' % key in source or 'youtu.be/embed/%s' % key in source \
                    or ('http://www.youtube.com/player_api' in source and "videoId: '%s'" % key in source):
                res = True
        browser.quit()
    except WebDriverException:
        print('task_check_this_url have WebDriverException on: ' + url_template)

    return res

@app.task()
def task_check_url_and_add_to_UrlGenerator(url_template):
    res = False
    if len(UrlGenerator.objects.filter(url=url_template)) == 0 and task_check_this_url(url_template):
        UrlGenerator.objects.create(url=url_template, active=True)
        res = True
    return res

@app.task()
def task_get_youtube_keys_and_slugs(key):
    yt_url = 'https://www.youtube.com/watch?v=%s' % key
    res = []

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (get_useraget())
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)
    browser.implicitly_wait(2)

    browser.get(yt_url)
    time.sleep(2)

    source = browser.page_source

    browser.quit()

    soup = BeautifulSoup(source, 'lxml')
    desc  = soup.find('span', {'id': 'eow-title'}).getText().strip()
    views = soup.find('div', {'id': 'watch7-views-info'}).find('div', {'class': 'watch-view-count'}).getText().replace(' views', '').replace(',', '').strip()
    views = int(views) if views.isdigit() else 0
    slug = slugify(desc, allow_unicode=True)
    slug2 = slugify(unidecode(desc), allow_unicode=False)
    res.append({'key': key, 'desc': desc, 'views': views, 'slug': slug, 'slug2': slug2})

    looklike = soup.find_all('div', {'class': 'content-wrapper'})

    for ll in looklike:
        key = ll.find('a').get('href').replace('/watch?v=', '')
        views = ll.find('span', {'class': 'stat view-count'}).getText().replace(' views', '').replace(',', '').strip()
        views = int(views) if views.isdigit() else 0
        desc = ll.find('span', {'class': 'title'}).getText().strip()
        slug = slugify(desc, allow_unicode=True)
        slug2 = slugify(unidecode(desc), allow_unicode=False)
        res.append({'key': key, 'desc': desc, 'views': views, 'slug': slug, 'slug2': slug2})

    for instance in res:
        if len(SearchStack.objects.filter(key=instance['key'])) == 0:
            SearchStack.objects.create(key=instance['key'], desc=instance['desc'], views=instance['views'], slug=instance['slug'], slug_uni=instance['slug2'], processed=False)
            instance['created'] = True
        else:
            instance['created'] = False
    return res

@app.task(bind=True)
def task_key_search(self, key, stop_page=2, on_page=100):
    urls = []
    res = []


    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (get_useraget())
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap) #, service_args=service_args
    browser.implicitly_wait(3)
    source_list = []

    for start in range(0, stop_page*on_page, on_page):
        search_url = u'https://www.google.com.ua/search?q=%22'+key+'%22+-site:youtube.com+-site:facebook.com+-site:vk.com&safe=off&gbv=2&ei=94ZAXPG2DOfrrgTR4ImIAQ&num='+str(on_page)+'&start='+str(start)+'&sa=N&filter=0&ved=0ahUKEwixjqbb-fTfAhXntYsKHVFwAhE4ChDy0wMIPQ&biw=1680&bih=976'
        browser.get(search_url)
        time.sleep(randint(3, 15))
        source_list.append(browser.page_source)

    for source in source_list:
        soup = BeautifulSoup(source, 'lxml')
        div_r_all = soup.find_all('div', {'class': 'r'})
        for div_r in div_r_all:
            a = div_r.find('a')
            url = a.get('href')
            if len(url) > 10 and url not in urls:
                urls.append(urllib.parse.unquote(urllib.parse.unquote(url)))

    search_stack_instance = SearchStack.objects.get(key=key)
    start_num = len(SearchUrlStack.objects.filter(key=search_stack_instance))
    for url in urls:
        domain = get_domain_name(url)
        if len(url) > 500 or len(SearchUrlStack.objects.filter(domain=domain)) != 0 or len(StopDomain.objects.filter(domain=domain)) != 0:
            res.append({'url': url, 'created': False})
        else:
            try:
                SearchUrlStack.objects.create(key=search_stack_instance, url=url, domain=domain)
                res.append({'url': url, 'created': True})
            except:
                res.append({'url': url, 'created': False})
        self.update_state(meta=res)

    if len(SearchUrlStack.objects.filter(key=search_stack_instance)) > start_num:
        search_stack_instance.processed = True
        search_stack_instance.save()

    browser.quit()
    time.sleep(randint(20, 120))

    return res

@app.task(bind=True)
def task_test(self, key):

    return res

@app.task(soft_time_limit=60)
def test_the_url(url):
    res = {'source': None, 'error': None}

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (get_useraget())

    try:
        browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)
        browser.get(url)
        source = get_source_with_iframes(browser)
        if source:
            if browser.current_url == url and 'youtube.com/watch?v=' in source or 'youtube-nocookie.com/embed/' in source \
                    or 'youtube.com/embed/' in source or 'youtu.be/' in source or ('youtube.com/player_api' in source and 'videoId:' in source):
                res['source'] = browser.page_source
            elif browser.current_url == url and 'ytapi.com/embed/' in source:
                res['error'] = 'ytapi.com - url -  No ditect youtube-video link'
            else:
                time.sleep(5)
                if browser.current_url == url and 'youtube.com/watch?v=' in source or 'youtube-nocookie.com/embed/' in source \
                        or 'youtube.com/embed/' in source or 'youtu.be/' in source or ('youtube.com/player_api' in source and 'videoId:' in source):
                    res['source'] = browser.page_source

        browser.quit()
    except WebDriverException:
        print("failed to start driver at " + url)
        res['error'] = "failed to start driver at " + url

    return res['source'], res['error']

@app.task(soft_time_limit=60)
def get_source_with_iframes(browser):
    source = browser.page_source
    if source:
        source = str(source)
        list = browser.find_elements_by_tag_name('iframe')
        if len(list) > 0:
            for iframe in list:
                try:
                    browser.switch_to.frame(iframe)
                    source += browser.page_source
                    browser.switch_to.default_content()
                except WebDriverException:
                    print('------------------ Iframe add to source error at: tasks.py - get_source_with_iframes')
    else:
        source = ''

    return source

@app.task()
def task_parse_url(key, slug, slug_uni, url):
    slug = slug or 'xxx-xxxx-xxxxx-xxxxxxx'
    slug_uni = slug_uni or 'xxx-xxxx-xxxxx-xxxxxxx'

    res = {'url': None, 'need_manual_check': False, 'error': None}
    v_args = ['?v=', 'id=', 'video=', 'video-', '?q=', 'download-', 'download=']
    v_separs = ['detail', 'video', 'watch', 'show', 'download', 'download-music', 'music', 'videodek', 'embed', 'embeded', 'mobile', 'code',
                'view', 'baixar', 'play', 'movies', 'search', 'tv', 'getvideo', 'get', 'mp3', 'src', 'lagu', 'related', 'video-dl', 'key',
                '!key!', '!-key!', '!key|lowercase!', '!anc!']
    url_obj = UrlConstructor(url)

    if len(StopDomain.objects.filter(domain=url_obj.domain)) != 0 or url_obj.domain in UrlGenerator.domains.domeins_all():       #If we worked with tis domain before
        print(url, 'This url is in StopDomain or alredy in our base. DELETED all urls witt this domain from UrlStack!!!')
        res['error'] = 'This url is in StopDomain or alredy in our base. URL DELETED'
        SearchUrlStack.objects.filter(url=url).delete()

        return res

    else:

        source_result, res['error'] = test_the_url(url)                                                                            #test if url is working and get page source

        if res['error']:
            print(url, 'URL Open Error in test_the_url(url)')
            return res
        elif not source_result:                                                                                    #if not working
            print(url, 'URL IS NOT WORKING NOW.')
            sso = SearchUrlStack.objects.get(url=url)
            sso.attempt +=1
            sso.save()
            if sso.attempt > 3:
                SearchUrlStack.objects.filter(domain=url_obj.domain).delete()
                res['error'] = 'URL IS NOT WORKING NOW. 3 attemprs gone - URL DELETED'
            else:
                res['error'] = 'URL IS NOT WORKING NOW.'

            return res

        else:                                                                                                        #START parsing
            print(url, 'START')
            print('FAZE 1 find key --------------------------------')                                               # trying to find a !key!

            tmp_res = None
            if url_obj.url.find(key) != -1:
                check_url = url_obj.url.replace(key, '!key!')
                if task_check_this_url(check_url):
                    tmp_res = check_url
                else:
                    res['error'] = 'Have exact key match in url, but url does not work'
            elif not tmp_res and url_obj.url.find(''.join(reversed(key))) != -1:
                check_url = url_obj.url.replace(''.join(reversed(key)), '!-key!')
                if task_check_this_url(check_url):
                    tmp_res = check_url
                else:
                    res['error'] = 'Have exact key match in url, but url does not work'
            elif not tmp_res and url_obj.url.find(key.lower()) != -1:
                check_url = url_obj.url.replace(key.lower(), '!key|lowercase!')
                if task_check_this_url(check_url):
                    tmp_res = check_url
                else:
                    res['error'] = 'Have exact key match in url, but url does not work'
            elif not tmp_res and len(url_obj.separate_11_list) > 0:                                             # if we have /key/ - like parts in url
                for str_11 in url_obj.separate_11_list:
                    if not tmp_res and task_check_this_url(str(url_obj.url).replace(str_11, '!key!')):
                        tmp_res = url_obj.url.replace(str_11, '!key!')

                    elif not tmp_res and task_check_this_url(str(url_obj.url).replace(str_11, '!-key!')):
                        tmp_res = url_obj.url.replace(str_11, '!-key!')

                    elif not tmp_res and task_check_this_url(str(url_obj.url).replace(str_11, '!key|lowercase!')):
                        tmp_res = url_obj.url.replace(str_11, '!key|lowercase!')

            elif not tmp_res and len(find_x_from_list_in_url(url, v_args)) > 0:                                 # if we have v_arg in url
                for item in find_x_from_list_in_url(url, v_args):
                    test_arg = url[url.find(item)+len(item): url.find(item)+len(item)+11]

                    if not tmp_res and task_check_this_url(url_obj.url.replace(test_arg, '!key!')):
                        tmp_res = url_obj.url.replace(test_arg, '!key!')

                    elif not tmp_res and task_check_this_url(url_obj.url.replace(test_arg, '!-key!')):
                        tmp_res = url_obj.url.replace(test_arg, '!-key!')

                    elif not tmp_res and task_check_this_url(url_obj.url.replace(test_arg, '!key|lowercase!')):
                        tmp_res = url_obj.url.replace(test_arg, '!key|lowercase!')
            # add if we have keys from source in url

            print('FAZE 2 find !anc! --------------------------------', tmp_res)

            if not tmp_res:                                                     # Have a !key!, nead to find !anc!
                StopDomain.objects.create(domain=get_domain_name(url), url=url[0:510], reason='DO NOT HAVE A KEY -- HAVE NO IDEA WHAT TO DO')
                SearchUrlStack.objects.filter(domain=get_domain_name(url)).delete()
                if res['error']:
                    res['error'] += 'DO NOT HAVE A KEY -- HAVE NO IDEA WHAT TO DO'
                else:
                    res['error'] = 'DO NOT HAVE A KEY -- HAVE NO IDEA WHAT TO DO'
                return res

            else:
                print(res['url'], tmp_res, 'Have !key!, start looking for anc')
                url_obj = UrlConstructor(tmp_res)
                check_url = tmp_res


                if not res['url'] and url_obj.url.lower().find(slug) != -1:
                    fragment = url_obj.url[url_obj.url.lower().find(slug):url_obj.url.lower().find(slug)+len(slug)]
                    check_url = url_obj.url.replace(fragment, '!anc!')
                    if task_check_this_url(check_url):
                        res['url'] = check_url
                    else:
                        res['error'] = 'Have exact slug match in url, but url does not work with !anc!'
                elif not res['url'] and url_obj.url.lower().find(slug_uni) != -1:
                    fragment = url_obj.url[url_obj.url.lower().find(slug_uni):url_obj.url.lower().find(slug)+len(slug_uni)]
                    check_url = url_obj.url.replace(fragment, '!anc!')
                    if task_check_this_url(check_url):
                        res['url'] = check_url
                    else:
                        res['error'] = 'Have exact slug_uni match in url, but url does not work with !anc!'
                elif not res['url'] and len(url_obj.separate_long_list) != 0:                                                          # we have to look for !anc!
                    for part in url_obj.separate_long_list:
                        if part.find('!key!') == -1 and part.find('!-key!') == -1 and part.find('!key|lowercase!') == -1:
                            print('Part with no key', part)
                            check_url = url_obj.url.replace(part, '!anc!')
                            if task_check_this_url(check_url):
                                res['url'] = check_url
                                break
                        else:
                            print('trying to parse part with key ********* ATTENTION!!!')
                            in_this_part = find_x_from_list_in_url(part, ['!key!', '!-key!', '!key|lowercase!'])[0]
                            print('in_this_part', in_this_part, part)
                            check_url = str(url_obj.url).replace(part, '!anc!-%s' % in_this_part)
                            if task_check_this_url(check_url):
                                res['url'] = check_url
                                break
                            check_url = str(url_obj.url).replace(part, '%s-!anc!' % in_this_part)
                            if task_check_this_url(check_url):
                                res['url'] = check_url
                                break

                            if part.find(in_this_part) > 1:
                                check_url = str(url_obj.url).replace(part[:part.find(in_this_part)-1], '!anc!')
                                if task_check_this_url(check_url):
                                    res['url'] = check_url
                                    break
                            if part.find(in_this_part) < len(part)-len(in_this_part):
                                check_url = str(url_obj.url).replace(part[part.find(in_this_part)+1:], '!anc!')
                                if task_check_this_url(check_url):
                                    res['url'] = check_url
                                    break
                    if not res['url']:
                        res['need_manual_check'] = True


                if not res['url'] and res['need_manual_check']:
                    res['url'] = tmp_res
                    print('RESULT: ', res['url'],  'BUT IT NEAD MANUAL CHECK')
                elif not res['url'] and not res['error']:
                    res['url'] = tmp_res
                    print('RESULT: ', res['url'],  'added after anc where not found')
                else:
                    res['url'] = tmp_res
                    res['need_manual_check'] = True

        if res['url'] and len(res['url']) > 198:
            res['url'] = None
            res['error'] = "URL Parcing error! Url len() after parcing > 200!! REsult discarded"
            print("URL Parcing error! Url len() after parcing > 200!! REsult discarded")
        elif res['url'] and not res['error']:
            UrlGenerator.objects.create(url=res['url'], active=True, need_review=res['need_manual_check'])
            SearchUrlStack.objects.filter(url=url).delete()
            print('Result is removed from UrlStack and added to our base! SUCCSESS!!!!!*********')
        elif not res['url'] and not res['error']:
            res['error'] = 'Do not have error or  url on Parse End'
        else:
            print('************************** Looks like we have some ERROR ***********************')

        print(res)
        return res
