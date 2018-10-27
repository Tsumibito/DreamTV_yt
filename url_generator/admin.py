from django.contrib import admin
from url_generator.models import UrlGenerator, UrlGeneratorTask, LoadFile, LoadFileData



class UrlGeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_anc', 'active')

class UrlGeneratorTaskAdmin(admin.ModelAdmin):
    list_display = ('date', 'youtube_key', 'youtube_url')

admin.site.register(UrlGenerator, UrlGeneratorAdmin)
admin.site.register(UrlGeneratorTask, UrlGeneratorTaskAdmin)
admin.site.register(LoadFile)
admin.site.register(LoadFileData)