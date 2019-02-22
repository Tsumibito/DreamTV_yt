from django.db import models
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files.storage import default_storage


class UrlGeneratorManager(models.Manager):
    def domeins_all(self):
        domeins = []
        for url in self.all():
            domeins.append(url.name)
        return domeins

class UrlGeneratorObjectsManager(models.Manager):
    def objects_all(self):
        return self.all()


class UrlGenerator(models.Model):                       #список урлов
    date_created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(unique=True)
    need_review = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    date_inactive = models.DateTimeField(blank=True, null=True)
    domains = UrlGeneratorManager()
    objects = UrlGeneratorObjectsManager()

    def __str__(self):
        return self.url

    @property
    def name(self):
        name = ''
        for i in str(self.url).replace('http://', '').replace('https://', ''):
            if i != '/':
                name = name + i
            else:
                break
        return name

    @property
    def is_anc(self):
        if str(self.url).find('!anc!') != -1:
            return True
        else:
            return False

class StopDomainManager(models.Manager):
    def domeins_all(self):
        domeins = []
        for domain in self.all():
            domeins.append(domain.domain)
        return domeins

class StopDomainObjectsManager(models.Manager):
    def objects_all(self):
        return self.all()

class StopDomain(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    domain = models.CharField(max_length=64, verbose_name=u'Domain name')
    url = models.CharField(max_length=512, verbose_name=u'Url that where baned',null=True, blank=True)
    reason = models.CharField(max_length=256, verbose_name=u'Bane reason or error',null=True, blank=True)
    domains = StopDomainManager()
    objects = StopDomainObjectsManager()

    def __str__(self):
        return self.domain

class SearchStackManager(models.Manager):
    def keys_all(self):
        keys = []
        for key in self.all():
            keys.append(key.key)
        return keys

class SearchStackObjectsManager(models.Manager):
    def objects_all(self):
        return self.all()

class SearchStack(models.Model):
    key = models.CharField(max_length=11, verbose_name=u'Youtube key')
    desc = models.CharField(max_length=256, verbose_name=u'Youtube desc', blank=True, null=True)
    slug = models.CharField(max_length=256, verbose_name=u'slug', blank=True, null=True)
    slug_uni = models.CharField(max_length=256, verbose_name=u'slug_unicode_safe', blank=True, null=True)
    views = models.IntegerField(blank=True, null=True, default=0)
    processed = models.BooleanField(default=False)
    keys = SearchStackManager()
    objects = SearchStackObjectsManager()

    def __str__(self):
        return self.key

class SearchUrlStack(models.Model):
    key = models.ForeignKey(SearchStack, blank=True, null=True, default=None, on_delete=models.CASCADE)
    url = models.CharField(max_length=512, verbose_name=u'URL')
    domain = models.CharField(max_length=64, verbose_name=u'Domain name', blank=True, null=True)
    attempt = models.IntegerField(blank=True, null=True, default=0)
    checked_light = models.BooleanField(default=False)
    checked_full = models.BooleanField(default=False)

    def __str__(self):
        return self.url


class UrlGeneratorTask(models.Model):                   # Список заданий
    date = models.DateTimeField(auto_now_add=True)
    youtube_url = models.CharField(max_length=128, verbose_name=u'YouTube URL (!Not youtu.be !)')
    description = models.TextField(blank=True, null=True, verbose_name=u'Вариативный анкор []-перемешать {}-выбрать')
    desc_variations = models.PositiveSmallIntegerField(blank=True, null=True, default='1', verbose_name=u'Число создаваемых вариаций анкора', help_text=u"Введите жалаемое число создаваемых вариаций анкора")
    links_number = models.IntegerField(blank=True, null=True, default='0')
    results = models.TextField(null=True, blank=True)
    #errors = models.ForeignKey(ErrorsUrl, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date)

    def youtube_key(self):
        return self.youtube_url.replace('https://www.youtube.com/watch?v=', '')

    def youtube_key_reverse(self):
        return ''.join(reversed(self.youtube_key()))

    def youtube_key_lower(self):
        return self.youtube_key().lower()

