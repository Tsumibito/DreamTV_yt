from django.shortcuts import render, redirect
from url_generator.random_text import give_me_rand_text_set
from url_generator.models import UrlGeneratorTask, SearchStack, SearchUrlStack
from url_generator.forms import UrlGeneratorTaskModelForm, AddUrlsForm, AddSearchUrlsForm, ParseUrlsForm
from django.utils.text import slugify

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from DreamTV_world.tasks import task_check_UrlGenerator_url, task_check_url_and_add_to_UrlGenerator, task_key_search, task_parse_url
from celery.result import AsyncResult
import celery
from celery import uuid
from urllib.parse import quote, unquote

from url_generator.utils import *


def generator_settings(request):
    context = {}
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
                        url_generator_task.links_number += 1
                else:
                    tmp_url =insert_data_in_url(str(my_url), url_generator_task.youtube_key())
                    url_generator_task.results += create_url_html_link(tmp_url)
                    url_generator_task.links_number += 1
            url_generator_task.save()
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

def add_search_urls(request):
    context = {}
    context_results = {'key': '', 'slug': '', 'task': '', 'errors': ''}
    if request.method == 'POST':
        form = AddSearchUrlsForm(request.POST)
        if form.is_valid():
            instance = form.cleaned_data
            key = instance['key']
            slug = instance['description']

            if key not in SearchStack.keys.keys_all():
                context_results['key'] = key
                context_results['slug'] = slug
                print(key, 'trying to parse search')
                search_res_task = task_key_search.delay(key, slug, stop_page=3, on_page=100)
                context_results['task'] = str(search_res_task.task_id)

            else:
                print(key, '- is already in list')
                context_results['errors'] = 'KEY %s ALREADY IN OUR LIST' % key


            request.session['context_data'] = context_results
            return redirect('url_generator:add_search_urls_results')

    form = AddSearchUrlsForm()
    context['form'] = form
    return render(request, 'url_generator/add_search_urls.html', context)


def add_search_urls_results(request):
    context = request.session.get('context_data')
    print(context)

    return render(request, 'url_generator/add_search_urls_results.html', context)

class AddSearchUrlsProcessor(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.BasePermission, )

    def get(self, request):
        res = {}
        context_data = request.session.get('context_data')
        if 'task' in context_data:
             curunt_task = AsyncResult(context_data['task'])
             res['task'] =  str(curunt_task.task_id)
             res['status'] = str(curunt_task.status)
             try:
                res['result'] = curunt_task.info
             except TypeError:
                res['result'] = str(curunt_task.info)
                print('Type error in AddSearchUrlsProcessor')

        return Response(res)


def sus_domains(request):           # Test code view

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
            slug = SearchStack.objects.get(key=str(key)).slug
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
                    task = task_parse_url.delay(key, slug, url)
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
        print(context_data)
        if 'parse_tasks' in context_data:
            for task_dic in context_data['parse_tasks']:
                res = {}
                task = AsyncResult(task_dic['task'])
                res['url'] = task_dic['url']
                res['task'] = str(task.task_id)
                res['status'] = str(task.status)
                res['result'] = task.info
                res_list.append(res)

        return Response(res_list)

