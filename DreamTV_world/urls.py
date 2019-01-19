from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path(r'^projects/', include('prj_manager.urls', namespace='prj_manager')),
    path('generator/', include('url_generator.urls', namespace='url_generator')),
    path('admin/', admin.site.urls),
    re_path(r'^api-auth/', include('rest_framework.urls')),
    re_path(r'^upload/', include('django_file_form.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


