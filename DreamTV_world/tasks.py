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
from DreamTV_world.task_utils import *
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
            if browser.current_url == url and 'ytapi.com/embed/' in source:
                res['error'] = 'ytapi.com - url -  No ditect youtube-video link'
            elif browser.current_url == url and 'youtube.com/watch?v=' in source or 'youtube-nocookie.com/embed/' in source \
                    or 'youtube.com/embed/' in source or 'youtu.be/' in source or ('youtube.com/player_api' in source and 'videoId:' in source):
                res['source'] = browser.page_source
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
    url_obj = UrlConstructor(url)
    res = {'url': None, 'need_manual_check': False, 'error': url_is_valid(url_obj)}

    if res['error']:
        print(url, 'URL is not valid - %s' % url)
        return res

    tmp_res, res['error'] = find_key_in_url(url, key)

    if tmp_res:
        res['url'], res['need_manual_check'], res['error'] = find_anc_in_url(tmp_res, slug, slug_uni)

    if res['url'] and len(res['url']) < 198 and not res['error']:
        UrlGenerator.objects.create(url=res['url'], active=True, need_review=res['need_manual_check'])
        SearchUrlStack.objects.filter(url=url).delete()
    else:
        print('************************** Looks like we have some ERROR! Result discarded!***********************')

    print(res)
    return res
