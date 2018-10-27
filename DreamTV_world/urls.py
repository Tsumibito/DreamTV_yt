"""DreamTV_world URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path(r'^projects/', include('prj_manager.urls', namespace='prj_manager')),
    path('generator/', include('url_generator.urls', namespace='url_generator')),
    path('admin/', admin.site.urls),
    # path('fine-uploader/', include('django_fine_uploader.urls', namespace='django_fine_uploader')),
    re_path(r'^upload/', include('django_file_form.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


