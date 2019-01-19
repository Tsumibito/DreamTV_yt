from django.contrib import admin
from url_generator.models import UrlGenerator, UrlGeneratorTask, StopDomain, SearchStack, SearchUrlStack


class UrlGeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_anc', 'date_created', 'active', 'need_review')

class UrlGeneratorTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'youtube_key', 'youtube_url')

class SearchUrlStackAdmin(admin.ModelAdmin):
    list_display = ('domain', 'url', 'key')

admin.site.register(UrlGenerator, UrlGeneratorAdmin)
admin.site.register(UrlGeneratorTask, UrlGeneratorTaskAdmin)
admin.site.register(StopDomain)
admin.site.register(SearchStack)
admin.site.register(SearchUrlStack, SearchUrlStackAdmin)
