from datetime import datetime, timedelta
from django.utils import timezone
from selenium import webdriver
from url_generator.models import UrlGenerator, StopDomain
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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

def get_source_with_iframes(browser):
    source = browser.page_source
    list = browser.find_elements_by_tag_name('iframe')
    for iframe in list:
        browser.switch_to.frame(iframe)
        source += browser.page_source
        browser.switch_to.default_content()
    return source


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

    # def check_var(self, separate_index, arg):
    #     res = None
    #     self.separate[separate_index] = arg
    #     url = insert_data_in_url(self.construct(), key)
    #     if check_this_url(url, key, desc) == True:
    #         res = self.construct()
    #     return res

    # def analize_min(self):
    #     res = None
    #
    #     print('in analize_min', self.url, self.skey, self.sanc)
    #     tmp = self.url
    #     tmp = tmp.replace(self.skey, '!key!').replace(''.join(reversed(self.skey)), '!-key!') \
    #         .replace(self.skey.lower(), '!key|lowercase!').replace(self.sanc, '!anc!')
    #     print(tmp, check_this_url(insert_data_in_url(tmp, key), key, desc))
    #
    #     if check_this_url(insert_data_in_url(tmp, key), key, desc) == True:
    #         self.result = tmp
    #         print('analize_min First result is ok', tmp)
    #         return self.result
    #
    #     elif len(self.separate) == 1 and len(self.separate[0]) == 11:
    #         print('in analize len(self.separate) == 1, key')
    #         self.result = self.check_var(0, '!key!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!-key!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!key|lowercase!')
    #         if  self.result != None:
    #             return self.result
    #
    #     elif len(self.separate) == 1 and len(self.separate[0]) > 11:
    #         print('in analize 1 url v2')
    #         tmp = self.separate[0]
    #
    #         self.result = self.check_var(0, '!key!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!anc!-!key!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!anc!-!-key!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!anc!-!key|lowercase!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!key!-!anc!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!-key!-!anc!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!key|lowercase!-!anc!')
    #         if  self.result != None:
    #             return self.result
    #
    #         self.result = self.check_var(0, '!anc!(!key!)')
    #         if  self.result != None:
    #             return res
    #
    #     else:
    #         return self.result
    #
    #
    #
    # def analize_full(self):
    #     res = None
    #     v_args = ['?v=', 'id=', 'video=', 'video-', '?q=', 'download-', 'download=']
    #     v_separs = ['detail', 'video', 'watch', 'show', 'download', 'download-music', 'music', 'videodek', 'embed', 'embeded', 'mobile', 'code',
    #                 'view', 'baixar', 'play', 'movies', 'search', 'tv', 'getvideo', 'get', 'mp3', 'src', 'lagu', 'related', 'video-dl', 'key',
    #                 '!key!', '!-key!', '!key|lowercase!', '!anc!']
    #
    #     print('in analize_full', self.url, len(self.separate), self.separate)
    #
    #     no_key = True
    #     for num, sp in enumerate(self.separate):
    #         if len(sp) <= 3 or sp.lower() in v_separs:
    #             pass
    #         elif len(sp) == 11 and sp.lower() not in v_separs:
    #             if  self.check_var(num, '!key!'):
    #                 self.separate[num] = '!key!'
    #                 no_key = False
    #             elif self.check_var(num, '!-key!') and no_key == True:
    #                 self.separate[num] = '!-key!'
    #                 no_key = False
    #             elif self.check_var(num, '!key|lowercase!') and no_key == True:
    #                 self.separate[num] = '!key|lowercase!'
    #                 no_key = False
    #         elif len(sp) > 11:
    #             for i in v_args:
    #                 if self.separate[num].find(i) != -1 and no_key == True:
    #                     tmp = self.separate[num].replace(self.separate[num][self.separate[num].find(i)+len(i):self.separate[num].find(i)+len(i)+11], '!key!')
    #                     res = self.check_var(num, '!key!')
    #                     if res != None:
    #                         self.separate[num] = tmp
    #                         no_key = False
    #                 if no_key == True:
    #                     tmp = self.separate[num].replace(self.separate[num][self.separate[num].find(i)+len(i):self.separate[num].find(i)+len(i)+11], '!-key!')
    #                     res = self.check_var(num, '!-key!')
    #                     if res != None:
    #                         self.separate[num] = tmp
    #                         no_key = False
    #                 if no_key == True:
    #                     tmp = self.separate[num].replace(self.separate[num][self.separate[num].find(i)+len(i):self.separate[num].find(i)+len(i)+11], '!key|lowercase!')
    #                     res = self.check_var(num, '!key|lowercase!')
    #                     if res != None:
    #                         self.separate[num] = tmp
    #                         no_key = False
    #
    #     print('NO KEY =', no_key)
    #
    #     for num, sp in enumerate(self.separate):
    #         if len(sp) > 11 and no_key == False and sp.find(self.sanc) != -1:
    #             tmp = self.separate[num].replace(self.sanc, '!anc!')
    #             self.check_var(num, tmp)
    #             if  res != None:
    #                 return res
    #         elif len(sp) > 11 and no_key == False:
    #             print('I am in checker !anc!')
    #             self.check_var(num, '!anc!')
    #             if  res != None:
    #                 return res
    #         elif len(sp) > 11 and no_key == True:
    #             print('I am in checker !anc!-!key!', num)
    #             res = self.check_var(num, '!anc!-!key!')
    #             if  res != None:
    #                 return res
    #
    #
    #             print('I am in checker !anc!-!-key!', num)
    #             res = self.check_var(num, '!anc!-!-key!')
    #             if  res != None:
    #                 return res
    #
    #             res = self.check_var(num, '!anc!-!key|lowercase!')
    #             if  res != None:
    #                 return res
    #
    #             res = self.check_var(num, '!key!-!anc!')
    #             if  res != None:
    #                 return res
    #
    #             res = self.check_var(num, '!-key!-!anc!')
    #             if  res != None:
    #                 return res
    #
    #             res = self.check_var(num, '!key|lowercase!-!anc!')
    #             if  res != None:
    #                 return res
    #
    #             res = self.check_var(num, '!anc!(!key!)')
    #             if  res != None:
    #                 return res
    #
    #             res = self.check_var(num, '!anc![!key!]')
    #             if  res != None:
    #                 return res
    #
    #             for i in v_args:
    #                 if self.separate[num].find(i) != -1:
    #                     res = self.check_var(num, self.separate[num].replace(self.separate[num][self.separate[num].find(i)+len(i):self.separate[num].find(i)+len(i)+11], '!key!'))
    #                     if res != None:
    #                         return res
    #
    #                     res = self.check_var(num, self.separate[num].replace(self.separate[num][self.separate[num].find(i)+len(i):self.separate[num].find(i)+len(i)+11], '!-key!'))
    #                     if res != None:
    #                         return res
    #
    #                     res = self.check_var(num, self.separate[num].replace(self.separate[num][self.separate[num].find(i)+len(i):self.separate[num].find(i)+len(i)+11], '!key|lowercase!'))
    #                     if res != None:
    #                         return res
    #
    #         if no_key == False:
    #             res = self.construct()
    #             return res
    #
    #     else:
    #         return res




def url_processor(urls, skey='4pCD17L_bRE', sanc='xxxx-xxxx-xxxx-xxxx-4321-xxxx'):
    domains_stop_list = StopDomain.domains.domeins_all()
    url_generator_domains = UrlGenerator.domains.domeins_all()
    results = []
    results_domains = []
    manual_review = []

    print(urls)

    for url in urls:
        print(url)

        if get_domain_name(url) not in url_generator_domains \
                and get_domain_name(url) not in domains_stop_list \
                and get_domain_name(url) not in results_domains:
            analize = UrlConstructor(url, skey, sanc)
            if analize.analize_min() != None:
                results.append(analize.result)
                results_domains.append(analize.domain)
                UrlGenerator.objects.create(url=analize.result, active=True)
                print('**************** Ready: ' + str(analize.result))
            elif analize.analize_full() != None:
                results.append(analize.result)
                results_domains.append(analize.domain)
                UrlGenerator.objects.create(url=analize.result, active=True)
                print('**************** Ready: ' + str(analize.result))
            else:
                manual_review.append(url)
                results_domains.append(analize.domain)
                StopDomain.objects.create(domain=analize.domain)
                print('**************** Manual Rewiew ' + url + ' = ' + str(analize.result))

        else:
            print('-- Pass: ' + url)

    return results, manual_review



