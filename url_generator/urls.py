from django.conf.urls import url
from django.urls import include, path, re_path
from url_generator import views
from django.conf.urls.static import static
from django.conf import settings
#from django.views.generic import RedirectView


app_name = 'url_generator'
urlpatterns = [
    path('', views.generator_settings, name='generator_settings'),
    path('up/', views.ExampleFormView.as_view(), name='upload_file'),
    re_path(r'^(?P<id>[0-9]+)/$', views.generator_results, name='generator_res'),
    #path('ex/', view=views.ExampleView.as_view(), name='home'),
    #path('ex/upload-1/', view=views.MyAppUploaderView.as_view(), name='uploader-1'),
    #path('ex/upload-2/', view=views.NotConcurrentUploaderView.as_view(), name='uploader-2'),
    #path('ex/upload-3/', view=views.SimpleCustomUploaderView.as_view(), name='uploader-3'),
    #path('ex/upload-4/', view=views.CustomFineUploaderView.as_view(), name='uploader-4'),
    ] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# url(r'^$', RedirectView.as_view(url='/UA/')),
# url(r'^(?P<lang>UA|RU|EN)/$', views.lead, name='lead'),
# url(r'^breaf/(?P<lang>UA|RU|EN)/(?P<id>[0-9]+)/$', views.breafme, name='breaf'),
# url(r'^thankyou/(?P<lang>UA|RU|EN)/(?P<id>[0-9]+)/$', views.thankyou, name='thankyou'),
# url(r'^confirm/(?P<lang>UA|RU|EN)/(?P<id>[0-9]+)/(?P<code>[0-9]+)/$', views.confirm, name='confirm'),
# url(r'^privacy-policy/(?P<lang>UA|RU|EN)/$', views.privacy, name='privacy')