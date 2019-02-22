from django.urls import include, path, re_path
from url_generator import views
from url_generator.views import CheckUrlsProcessor, AddUrlsProcessor, AddSearchKeysProcessor, AddSearchUrlsProcessor, ParseUrlsProcessor


app_name = 'url_generator'
urlpatterns = [
    path('', views.generator_settings, name='generator_settings'),
    path('check_urls/', views.check_urls, name='check_urls'),
    path('check_urls/list/', views.check_urls_list, name='check_urls_list'),
    path('check_urls/processor/', CheckUrlsProcessor.as_view(), name='check_urls_processor'),
    path('add_urls/', views.add_urls, name='add_urls'),
    path('add_urls/results/', views.add_urls_results, name='add_urls_results'),
    path('add_urls/processor/', AddUrlsProcessor.as_view(), name='add_urls_processor'),
    path('add_search_keys/', views.add_search_keys, name='add_search_keys'),
    path('add_search_keys/results/', views.add_search_keys_results, name='add_search_keys_results'),
    path('add_search_keys/processor/', AddSearchKeysProcessor.as_view(), name='add_search_keys_processor'),
    path('add_search_urls/', views.add_search_urls, name='add_search_urls'),
    path('add_search_urls/results/', views.add_search_urls_results, name='add_search_urls_results'),
    path('add_search_urls/processor/', AddSearchUrlsProcessor.as_view(), name='add_search_urls_processor'),

    path('sus_domains/', views.sus_domains, name='sus_domains'),
    path('parse_urls/', views.parse_urls, name='parse_urls'),
    path('parse_urls/results/', views.parse_urls_results, name='parse_urls_results'),
    path('parse_urls/processor/', ParseUrlsProcessor.as_view(), name='parse_urls_processor'),
    re_path(r'^(?P<id>[0-9]+)/$', views.generator_results, name='generator_res'),
    ]
