from django.contrib import admin
from url_generator.models import UrlGenerator, UrlGeneratorTask, StopDomain, SearchStack, SearchUrlStack


class UrlGeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_anc', 'date_created', 'active', 'need_review')
    actions = ['make_manual_viewed']

    def make_manual_viewed(self, request, queryset):
        queryset.update(need_review=False)
    make_manual_viewed.short_description = "Mark selected stories as viewed manually"

class UrlGeneratorTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'youtube_key', 'youtube_url')

class SearchUrlStackAdmin(admin.ModelAdmin):
    list_display = ('key', 'domain', 'url', 'attempt')

class SearchStackAdmin(admin.ModelAdmin):
    list_display = ('key', 'views', 'desc', 'processed')

class StopDomainAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'domain', 'reason', 'url')

admin.site.register(UrlGenerator, UrlGeneratorAdmin)
admin.site.register(UrlGeneratorTask, UrlGeneratorTaskAdmin)
admin.site.register(StopDomain, StopDomainAdmin)
admin.site.register(SearchStack, SearchStackAdmin)
admin.site.register(SearchUrlStack, SearchUrlStackAdmin)
