from DreamTV_world.celery import app
from url_generator.utils import *
from selenium import webdriver
from url_generator.models import UrlGenerator, StopDomain, SearchUrlStack, SearchStack
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from random import randint
from celery.utils.log import get_task_logger

import time
# celery worker -A DreamTV_world --loglevel=debug --concurrency=4
# celery -f purge
# redis-cli flushall

logger = get_task_logger(__name__)

@app.task(default_retry_delay=60, max_retries=3, soft_time_limit=120)
def task_check_UrlGenerator_url(url_name):
    key = '4pCD17L_bRE'
    desc = 'Истоки философского мышления 4'
    url_instance = UrlGenerator.objects.get(url=url_name)

    url = insert_data_in_url(str(url_instance.url), key)
    res = False

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36")
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)

    browser.get(url)
    if browser.current_url == url and desc.lower() in browser.page_source.lower() and key in browser.page_source:
        res = True
    else:
        time.sleep(7)
        if browser.current_url == url and desc.lower() in browser.page_source.lower() and key in browser.page_source:
            res = True
        elif browser.current_url != url and url.replace(get_http_and_domain(url), get_http_and_domain(browser.current_url)) == browser.current_url \
                and desc.lower() in browser.page_source.lower() and key in browser.page_source:
            url_instance.url = str(url_instance.url).replace(get_http_and_domain(url), get_http_and_domain(browser.current_url))
            url_instance.save()
            res = True
        elif browser.current_url != url and desc.lower() in browser.page_source.lower() and key in browser.page_source:
            url_instance.need_review = True
            url_instance.save()

    if res:
        activate_url(url_instance)
    else:
        logger.info(url_instance, 'url==url ', browser.current_url == url or browser.current_url == change_prefix(url),
              'desc in ps: ', desc.lower() in browser.page_source.lower(), 'key ib ps: ', key in browser.page_source, url,
              'brow curent url: ', browser.current_url)
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
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36")
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)

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
    return res

@app.task()
def task_check_url_and_add_to_UrlGenerator(url_template):
    res = False
    if len(UrlGenerator.objects.filter(url=url_template)) == 0 and task_check_this_url(url_template):
        UrlGenerator.objects.create(url=url_template, active=True)
        res = True
    return res

@app.task(bind=True)
def task_key_search(self, key, slug, stop_page=2, on_page=100):
    urls = []
    res = []

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36")
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)
    browser.implicitly_wait(5)
    source_list = []

    for start in range(0, stop_page*on_page, on_page):
        search_url = u'https://www.google.com.ua/search?q=%22'+key+'%22+-site:youtube.com+-site:facebook.com+-site:vk.com&safe=off&gbv=2&ei=94ZAXPG2DOfrrgTR4ImIAQ&num='+str(on_page)+'&start='+str(start)+'&sa=N&filter=0&ved=0ahUKEwixjqbb-fTfAhXntYsKHVFwAhE4ChDy0wMIPQ&biw=1680&bih=976'
        browser.get(search_url)
        time.sleep(randint(3, 15))
        source_list.append(browser.page_source)

    for source in source_list:
        soup = BeautifulSoup(source, 'lxml', from_encoding='utf-8')
        div_r_all = soup.find_all('div', {'class': 'r'})
        for div_r in div_r_all:
            a = div_r.find('a')
            url = a.get('href')
            if len(url) > 10 and url not in urls:
                urls.append(url)

    SearchStack.objects.create(key=key, slug=slug)
    search_stack_instance = SearchStack.objects.get(key=key)
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

    return res

@app.task(soft_time_limit=60)
def test_the_url(url):
    res = None

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36")
    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)

    browser.get(url)
    source = get_source_with_iframes(browser)
    if browser.current_url == url and 'youtube.com/watch?v=' in source or 'youtube-nocookie.com/embed/' in source \
            or 'youtube.com/embed/' in source or 'youtu.be/' in source or ('youtube.com/player_api' in source and 'videoId:' in source):
        res = browser.page_source
    else:
        time.sleep(5)
        if browser.current_url == url and 'youtube.com/watch?v=' in source or 'youtube-nocookie.com/embed/' in source \
                or 'youtube.com/embed/' in source or 'youtu.be/' in source or ('youtube.com/player_api' in source and 'videoId:' in source):
            res = browser.page_source

    browser.quit()
    return res

@app.task()
def task_parse_url(key, slug, url):
    logger.info(key, slug)
    res = {'url': None, 'need_manual_check': False, 'error': None}
    v_args = ['?v=', 'id=', 'video=', 'video-', '?q=', 'download-', 'download=']
    v_separs = ['detail', 'video', 'watch', 'show', 'download', 'download-music', 'music', 'videodek', 'embed', 'embeded', 'mobile', 'code',
                'view', 'baixar', 'play', 'movies', 'search', 'tv', 'getvideo', 'get', 'mp3', 'src', 'lagu', 'related', 'video-dl', 'key',
                '!key!', '!-key!', '!key|lowercase!', '!anc!']
    url_obj = UrlConstructor(url)

    if len(StopDomain.objects.filter(domain=url_obj.domain)) != 0 or url_obj.domain in UrlGenerator.domains.domeins_all():       #If we worked with tis domain before
        logger.info(url, 'This url is in StopDomain or alredy in our base. DELETED all urls witt this domain from UrlStack!!!')
        SearchUrlStack.objects.filter(domain=url_obj.domain).delete()
        res['error'] = 'This url is in StopDomain or alredy in our base'
        return res
    else:
        source_result = test_the_url(url)                                                                            #test if url is working and get page source

        if source_result == None:                                                                                    #if not working
            res['error'] = 'URL IS NOT WORKING NOW'
            logger.info(url, 'URL IS NOT WORKING NOW. May be next time!')
            return 'URL IS NOT WORKING NOW'
        else:                                                                                                        #START parsing
            logger.info(url, 'START')

            logger.info('FAZE 1 find key --------------------------------')                                               # trying to find a !key!
            tmp_res = None
            if url_obj.url.find(key) != -1 or url_obj.url.find(''.join(reversed(key))) != -1 or url_obj.url.find(key.lower()) != -1:
                check_url = str(url_obj.url).replace(key, '!key!').replace(''.join(reversed(key)), '!-key!').replace(key.lower(), '!key|lowercase!')
                if task_check_this_url(check_url) == True:
                    tmp_res = check_url
                    logger.info(tmp_res)
            elif tmp_res == None and len(url_obj.separate_11_list) > 0:                                             # if we have /key/ - like parts in url
                for str_11 in url_obj.separate_11_list:
                    if task_check_this_url(str(url_obj.url).replace(str_11, '!key!')) == True:
                        tmp_res = str(url_obj.url).replace(str_11, '!key!')
                        logger.info(tmp_res)
                    elif task_check_this_url(str(url_obj.url).replace(str_11, '!-key!')) == True:
                        tmp_res = str(url_obj.url).replace(str_11, '!-key!')
                        logger.info(tmp_res)
                    elif task_check_this_url(str(url_obj.url).replace(str_11, '!key|lowercase!')) == True:
                        tmp_res = str(url_obj.url).replace(str_11, '!key|lowercase!')
                        logger.info(tmp_res)
            elif tmp_res == None and len(find_x_from_list_in_url(url, v_args)) > 0:                                 # if we have v_arg in url
                for item in find_x_from_list_in_url(url, v_args):
                    test_arg = url[url.find(item)+len(item): url.find(item)+len(item)+11]
                    logger.info('test_arg:', test_arg)

                    if task_check_this_url(str(url_obj.url).replace(test_arg, '!key!')) == True:
                        tmp_res = str(url_obj.url).replace(test_arg, '!key!')
                        logger.info(tmp_res)
                    elif task_check_this_url(str(url_obj.url).replace(test_arg, '!-key!')) == True:
                        tmp_res = str(url_obj.url).replace(test_arg, '!-key!')
                        logger.info(tmp_res)
                    elif task_check_this_url(str(url_obj.url).replace(test_arg, '!key|lowercase!')) == True:
                        tmp_res = str(url_obj.url).replace(test_arg, '!key|lowercase!')
                        logger.info(tmp_res)
            # add if we have keys from source in url



            logger.info('FAZE 2 find !anc! --------------------------------', tmp_res)



            if tmp_res != None:                                                                                      # Have a !key!, nead to find !anc!
                url_obj = UrlConstructor(tmp_res)

                check_url = tmp_res
                if url_obj.url.find(slug) == -1 and len(url_obj.separate_long_list) == 0:                           # !anc! is impossible
                     res['url'] = check_url
                elif url_obj.url.find(slug) != -1:                                                                  # slug found in url
                    check_url = str(url_obj.url).replace(slug, '!anc!')
                    if task_check_this_url(check_url) == True:
                        res['url'] = check_url
                elif len(url_obj.separate_long_list) != 0:                                                          # we have to look for !anc!
                    for part in url_obj.separate_long_list:
                        if part.find('!key!') == -1 and part.find('!-key!') == -1 and part.find('!key|lowercase!') == -1:
                            logger.info('Part with no key', part)
                            check_url = str(url_obj.url).replace(part, '!anc!')
                            if task_check_this_url(check_url) == True:
                                res['url'] = check_url
                                break
                        else:
                            logger.info('trying to parse part with key ********* ATTENTION!!!')
                            in_this_part = find_x_from_list_in_url(part, ['!key!', '!-key!', '!key|lowercase!'])[0]
                            logger.info('in_this_part', in_this_part, part)
                            check_url = str(url_obj.url).replace(part, '!anc!-%s' % in_this_part)
                            if task_check_this_url(check_url) == True:
                                res['url'] = check_url
                                break
                            check_url = str(url_obj.url).replace(part, '%s-!anc!' % in_this_part)
                            if task_check_this_url(check_url) == True:
                                res['url'] = check_url
                                break

                            if part.find(in_this_part) > 1:
                                check_url = str(url_obj.url).replace(part[:part.find(in_this_part)-1], '!anc!')
                                if task_check_this_url(check_url) == True:
                                    res['url'] = check_url
                                    break
                            if part.find(in_this_part) < len(part)-len(in_this_part):
                                check_url = str(url_obj.url).replace(part[part.find(in_this_part)+1:], '!anc!')
                                if task_check_this_url(check_url) == True:
                                    res['url'] = check_url
                                    break


                    if res['url'] == None:
                        res['need_manual_check'] = True


                if res['url'] == None and res['need_manual_check'] == True:
                    res['url'] = tmp_res
                    logger.info('RESULT: ', res['url'],  'BUT IT NEAD MANUAL CHECK')
                elif res['url'] != None:
                    logger.info('RESULT: ', res['url'],  'It is OK !!!')
                else:
                    logger.info('RESULT: ', None,  'Nead more parsing........')

            else:
                logger.info('DO NOT HAVE A KEY -------------------------------- HAVE NO IDEA WHAT TO DO')


        logger.info(res)
        if res['url'] != None and len(res['url']) > 198:
            res['url'] = None
            res['error'] = "URL Parcing error! Url len() after parcing > 200!! REsult discarded"
            logger.info("URL Parcing error! Url len() after parcing > 200!! REsult discarded")
        elif res['url'] != None:
            UrlGenerator.objects.create(url=res['url'], active=True, need_review=res['need_manual_check'])
            SearchUrlStack.objects.filter(url=url).delete()
            logger.info('Result is removed from UrlStack and added to our base! SUCCSESS!!!!!*********')

        return res
