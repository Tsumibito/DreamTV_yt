from django.shortcuts import render, redirect
from url_generator.random_text import give_me_rand_text_set
from url_generator.models import UrlGeneratorTask, SearchStack, SearchUrlStack
from url_generator.forms import UrlGeneratorTaskModelForm, AddUrlsForm, AddSearchUrlsForm, ParseUrlsForm
from django.utils.text import slugify

from unidecode import unidecode

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from DreamTV_world.tasks import *
from celery.result import AsyncResult
import requests
import celery
from celery import uuid
from urllib.parse import quote, unquote
import codecs
import urllib

from url_generator.utils import *


def generator_settings(request):
    context = {}
    lp_urls = []
    url_list = UrlGenerator.objects.filter(active=True)
    context['active_count'] = len(url_list)

    if request.method == 'POST':
        form = UrlGeneratorTaskModelForm(request.POST)
        if form.is_valid():
            instance = form.save()
            url_generator_task = UrlGeneratorTask.objects.get(id=instance.id)
            desc_list = give_me_rand_text_set(url_generator_task.description, url_generator_task.desc_variations*3)
            url_generator_task.results = u''
            url_generator_task.links_number = 0
            for my_url in url_list:
                if '!anc!' in str(my_url):
                    desc_temp = set(desc_list)
                    for i in range(url_generator_task.desc_variations):
                        tmp_url = insert_data_in_url(str(my_url), url_generator_task.youtube_key(), slugify(desc_temp.pop().lower(), allow_unicode=True))
                        url_generator_task.results += create_url_html_link(tmp_url)
                        lp_urls.append(tmp_url)
                        url_generator_task.links_number += 1
                else:
                    tmp_url = insert_data_in_url(str(my_url), url_generator_task.youtube_key())
                    url_generator_task.results += create_url_html_link(tmp_url)
                    lp_urls.append(tmp_url)
                    url_generator_task.links_number += 1
            url_generator_task.save()

            key = '9834099457cd9c6386dab483c126e73a8db99129f591'
            proj_name = url_generator_task.youtube_key()
            dripfeed = 7
            urls = '|'.join(lp_urls[0:1999])
            params = {'apikey': key, 'proj_name': proj_name, 'dripfeed': dripfeed, 'urls': urls}
            linkprocessor = requests.post('https://api.linkprocessor.net/api.php', data=params)
            if linkprocessor.status_code != 200:
                (print(linkprocessor.status_code))
                (print(linkprocessor.content))
            else:

                (print(linkprocessor.content))

            return redirect('url_generator:generator_res', id=instance.id)
    else:
        form = UrlGeneratorTaskModelForm()
    context['form'] = form
    return render(request, 'url_generator/generator_settings.html', context)

def generator_results(request, id):
    instance = UrlGeneratorTask.objects.get(id=id)
    context = {'id': id}
    context['url'] = instance.youtube_url
    context['links_number'] = instance.links_number
    context['results'] = instance.results
    return render(request, 'url_generator/generator_results.html', context)

def check_urls(request):
    context = {'url_dics': [], 'count_urls': 0}
    url_list = UrlGenerator.objects.all()

    for url_instance in url_list:
        url_text = str(url_instance.url)
        curunt_task = task_check_UrlGenerator_url.delay(url_text)
        task_dic = {'url': url_text, 'task': str(curunt_task)}
        context['url_dics'].append(task_dic)
        context['count_urls'] += 1

    request.session['context_data'] = context

    return redirect('url_generator:check_urls_list')

def check_urls_list(request):
    context = request.session.get('context_data')

    return render(request, 'url_generator/check_urls_list.html', context)


class CheckUrlsProcessor(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.BasePermission, )

    def get(self, request):
        res = []
        context_data = request.session.get('context_data')
        if 'url_dics' in context_data:
            url_dics = context_data['url_dics']
            for url_dic in url_dics:
                curunt_task = AsyncResult(url_dic['task'])
                res.append({'url': url_dic['url'],
                            'task': str(curunt_task.task_id),
                            'status': str(curunt_task.status),
                            'result': str(curunt_task.info),
                            'test': insert_data_in_url(str(url_dic['url']), '4pCD17L_bRE') })
        return Response(res)

def add_urls(request):
    context = {}
    context_results = {'check_urls': [], 'check_urls_count': 0, 'have_urls': [], 'have_urls_count': 0}

    if request.method == 'POST':
        form = AddUrlsForm(request.POST)
        if form.is_valid():
            instance = form.cleaned_data
            for line in instance['urls_text_area'].splitlines():
                line = str(line).replace(' ', '')
                #url = insert_data_in_url(str(line), key)
                if len(UrlGenerator.objects.filter(url=line)) == 0:
                    curunt_task = task_check_url_and_add_to_UrlGenerator.delay(line)
                    task_dic = {'url': line, 'task': str(curunt_task)}
                    context_results['check_urls'].append(task_dic)
                    context_results['check_urls_count'] += 1
                else:
                    context_results['have_urls'].append(line)
                    context_results['have_urls_count'] += 1

            request.session['context_data'] = context_results
            return redirect('url_generator:add_urls_results')

    form = AddUrlsForm()
    context['form'] = form
    return render(request, 'url_generator/add_urls.html', context)

def add_urls_results(request):
    context = request.session.get('context_data')

    return render(request, 'url_generator/add_urls_results.html', context)

class AddUrlsProcessor(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.BasePermission, )

    def get(self, request):
        res = []
        context_data = request.session.get('context_data')
        if 'check_urls' in context_data:
            url_dics = context_data['check_urls']
            for url_dic in url_dics:
                curunt_task = AsyncResult(url_dic['task'])
                res.append({'url': url_dic['url'],
                            'task': str(curunt_task.task_id),
                            'status': str(curunt_task.status),
                            'result': str(curunt_task.info),
                            'test': insert_data_in_url(str(url_dic['url']), '4pCD17L_bRE') })
        return Response(res)

def add_search_keys(request):
    context = {}
    context_results = {'key': '', 'task': '', 'errors': ''}
    if request.method == 'POST':
        form = AddSearchUrlsForm(request.POST)
        if form.is_valid():
            instance = form.cleaned_data
            key = instance['key']
            task = task_get_youtube_keys_and_slugs.delay(key)
            context_results['key'] = key
            context_results['task'] = str(task)

            request.session['context_data'] = context_results
            return redirect('url_generator:add_search_keys_results')

    form = AddSearchUrlsForm()
    context['form'] = form
    return render(request, 'url_generator/add_search_keys.html', context)

def add_search_keys_results(request):
    context = request.session.get('context_data')

    return render(request, 'url_generator/add_search_keys_results.html', context)

class AddSearchKeysProcessor(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.BasePermission, )

    def get(self, request):
        res = {}
        context_data = request.session.get('context_data')
        if 'task' in context_data:
             curunt_task = AsyncResult(context_data['task'])
             res['task'] =  str(curunt_task.task_id)
             res['status'] = str(curunt_task.status)
             res['result'] = curunt_task.info

        return Response(res)

def add_search_urls(request):
    context_results = []

    for key_instance in SearchStack.objects.filter(processed=False)[0:5]:
        res_dic = {'errors': ''}
        res_dic['key'] = str(key_instance.key)
        task = task_key_search.delay(key_instance.key)
        res_dic['task'] = str(task)
        context_results.append(res_dic)

    request.session['context_data'] = {'context_results': context_results}
    return redirect('url_generator:add_search_urls_results')

def add_search_urls_results(request):
    context = request.session.get('context_data')

    return render(request, 'url_generator/add_search_urls_results.html', context)

class AddSearchUrlsProcessor(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.BasePermission, )

    def get(self, request):
        res = {}
        context_data = request.session.get('context_data')

        res_list = []
        for task_dic in context_data['context_results']:
            print(task_test)
            res = {}
            task = AsyncResult(task_dic['task'])
            res['key'] = task_dic['key']
            res['task'] = str(task.task_id)
            res['status'] = str(task.status)
            res['result'] = task.info
            res_list.append(res)

        return Response(res_list)


def sus_domains(request):           # Test code view
    res = {'url': None, 'need_manual_check': False, 'error': None}
    url = 'http://hotmusicleak.com/10-alternatif-rantai-salju-paling-menakjubkan-untuk-musim-dingin-ini/!key!.html'
    url_obj = UrlConstructor(url)
    slug = '10-most-amazing-snow-chain-alternatives-for-this-winter'
    tmp_res = None


    if not res['url'] and url_obj.url.lower().find(slug) != -1:
        fragment = url_obj.url[url_obj.url.lower().find(slug):url_obj.url.lower().find(slug)+len(slug)]
        check_url = url_obj.url.replace(fragment, '!anc!')
        if task_check_this_url(check_url):
            res['url'] = check_url
        else:
            res['error'] = 'Have exact slug match in url, but url does not work with !anc!'


    return redirect('url_generator:generator_settings')


def parse_urls(request):
    context = {}
    context_results = {}

    if request.method == 'POST':
        form = ParseUrlsForm(request.POST)
        if form.is_valid():
            urls = []
            instance = form.cleaned_data
            key = instance['chouce_key']
            serch_stack = SearchStack.objects.get(key=str(key))
            slug = serch_stack.slug
            slug_uni = serch_stack.slug_uni
            urls_filter = SearchUrlStack.objects.filter(key__key=key)
            if len(urls_filter) > 0:
                for url_instance in urls_filter:
                    urls.append(url_instance.url)
                urls_count = len(urls)
                context_results['key'] = key
                context_results['slug'] = slug
                context_results['urls_count'] = urls_count
                context_results['parse_tasks'] = []
                for url in urls:
                    task = task_parse_url.delay(key, slug, slug_uni, url)
                    context_results['parse_tasks'].append({'url': url, 'task': str(task), 'status': 'INITIALISING', 'result': None})
            else:
                print('Zero URLS are in this Key stack')

            request.session['context_parse_results'] = context_results
            return redirect('url_generator:parse_urls_results')

    form = ParseUrlsForm()
    context['form'] = form

    return render(request, 'url_generator/parse_urls.html', context)

def parse_urls_results(request):
    context = request.session.get('context_parse_results')

    return render(request, 'url_generator/parse_urls_results.html', context)

class ParseUrlsProcessor(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.BasePermission, )

    def get(self, request):
        res_list = []
        context_data = request.session.get('context_parse_results')
        #print(context_data)
        if 'parse_tasks' in context_data:
            #print(context_data['parse_tasks'])
            for task_dic in context_data['parse_tasks']:
                res = {}
                task = AsyncResult(task_dic['task'])
                res['url'] = task_dic['url']
                res['task'] = str(task.task_id)
                res['status'] = str(task.status)
                res['result'] = task.info
                res_list.append(res)

        return Response(res_list)

