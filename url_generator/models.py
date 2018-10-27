from django.db import models
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files.storage import default_storage



class UrlGenerator(models.Model):                       #список урлов
    url = models.URLField(unique=True)
    active = models.BooleanField(default=True)

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


class UrlGeneratorTask(models.Model):                   # Список заданий
    date = models.DateTimeField(auto_now_add=True)
    youtube_url = models.CharField(max_length=128, verbose_name=u'YouTube URL (!Not youtu.be !)')
    file = models.FileField(upload_to='prg1/', blank=True, null=True)
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


class LoadFile(models.Model):
    title = models.CharField(max_length=255)


class LoadFileData(models.Model):
    fs = default_storage

    load_file = models.ForeignKey(LoadFile, related_name='files', on_delete=models.CASCADE)
    input_file = models.FileField(upload_to='example', storage=fs)

    def __str__(self):
        return str(self.input_file)

