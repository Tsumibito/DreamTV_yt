from datetime import datetime, timedelta
from django.utils import timezone
from selenium import webdriver
from url_generator.models import UrlGenerator, StopDomain
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from random import randint

import time

key = '4pCD17L_bRE'
desc = 'Истоки философского мышления 4'

def deactivate_url(url_instance):
    print('------------------', timezone.now() - timedelta(days=7))
    url_instance.active = False
    if not url_instance.date_inactive:
        url_instance.date_inactive = timezone.now()
    elif url_instance.date_inactive > timezone.now() - timedelta(days=7):
        print('!!!!!DDDDDDDDD!!!!!! will be deleted soon: '+ str(url_instance))
    else:
        pass
    url_instance.save()

def activate_url(url_instance):
    url_instance.active = True
    url_instance.date_inactive = None
    url_instance.save()

def change_prefix(url):
    if url.find('https://') != -1:
        url = url.replace('https://', 'http://')
    elif url.find('http://') != -1:
        url = url.replace('http://', 'https://')
    return url

def check_this_url(url, key, desc):
    res = False

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36")

    browser = webdriver.PhantomJS('/Users/mymac/Downloads/phantomjs/bin/phantomjs', desired_capabilities=dcap)
    browser.get(url)
    #browser.save_screenshot('test321.png')
    print(browser.current_url)
    #print(browser.page_source)
    if browser.current_url == url:
        if desc in browser.page_source and key in browser.page_source:
            res = True
            print(res)
        else:
            time.sleep(7)
            if desc in browser.page_source and key in browser.page_source and browser.current_url == url:
                res = True

    print(desc in browser.page_source, key in browser.page_source, browser.current_url == url)
    browser.quit()
    return res

def insert_data_in_url(url_to_insert, key, anc='xxxx-xxxx'):
    return url_to_insert.replace('!key!', key).replace('!anc!', anc).replace('!-key!', ''.join(reversed(key))).replace('!key|lowercase!', key.lower())

def create_url_html_link(url, color='black'):
    return '<p><a target="_blank" style="color: ' + color +'" href="' + str(url) +'">' + str(url) +'</a></p>'

def get_domain_name(url):
    name = str(url).replace('http://', '').replace('https://', '')
    return name[0:name.find('/', 0, len(name))]

def get_http_and_domain(url):
    return str(url)[0:url.find('/', 8, len(url))]

def find_x_from_list_in_url(url, list):
    res = []
    for item in list:
        if url.find(item) != -1:
            res.append(item)
    return res

def lp_api_call(proj_name, dripfeed, urls):
    key = '9834099457cd9c6386dab483c126e73a8db99129f591'
    url = 'https://api.linkprocessor.net/api.php?apikey=%s&proj_name=%s&dripfeed=%d&urls=%s' % (key, proj_name, dripfeed, urls)
    return url

def get_useraget():
    with open('url_generator/useragents.json') as f:
        data = json.load(f)
        useragent = data[randint(0, len(data)-1)]


    return useragent


class UrlConstructor:
    def __init__(self, url):
        self.url = url
        self.url_modified = str(url)
        self.prefix = self.get_prefix()
        self.domain = self.get_domain()
        self.postfix = self.get_postfix()
        self.separate = self.do_separate()
        self.separate_count = len(self.separate)
        self.separate_11_list = self.get_separate_11_list()
        self.separate_long_list = self.get_separate_long_list()


    def get_prefix(self):
        if 'http://' in self.url:
            self.url_modified = self.url_modified.replace('http://', '')
            return 'http://'
        elif 'https://' in self.url:
            self.url_modified = self.url_modified.replace('https://', '')
            return 'https://'

    def get_domain(self):
        domain = get_domain_name(self.url_modified)
        self.url_modified = self.url_modified.replace( domain + '/', '')
        return domain

    def get_postfix(self):
        postfix = ''
        postfix_var = ['.html', '.video', '.txt', '.htm', '.php', '/', '.doc', '.video+related']
        for var in postfix_var:
            if self.url_modified[0 - len(var):len(self.url_modified)] == var:
                self.url_modified = self.url_modified[:0 - len(var)]
                postfix = var
                break
        return postfix

    def do_separate(self):
        return self.url_modified.split('/')

    def construct(self):
            return self.prefix + self.domain + '/' + '/'.join(self.separate) + self.postfix

    def get_separate_11_list(self):
        res = []
        for sep in self.separate:
            if len(sep) == 11:
                res.append(sep)
        return res

    def get_separate_long_list(self):
        res = []
        for sep in self.separate:
            if len(sep) > 11:
                res.append(sep)
        return res



