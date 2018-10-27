from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from url_generator.random_text import give_me_rand_text_set
from url_generator.models import UrlGeneratorTask, UrlGenerator, LoadFile, LoadFileData
from url_generator.forms import UrlGeneratorTaskModelForm, FileForm, ExistingFileForm
from b2blaze import B2
from url_generator.utils import handle_uploaded_file
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import random
import os
#from b2_storage.storage import B2Storage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


from django.views.decorators.csrf import csrf_exempt
from django_fine_uploader.fineuploader import SimpleFineUploader, ChunkedFineUploader
from django_fine_uploader.forms import FineUploaderUploadForm
from django_fine_uploader.views import FineUploaderView
from django.http import JsonResponse
from django.views import generic

from django.http import HttpResponseRedirect
from django_file_form.uploader import FileFormUploader


def generator_settings(request):
    context = {}

    if request.method == 'POST':
        form = UrlGeneratorTaskModelForm(request.POST, request.FILES)
        if form.is_valid():
            instance = UrlGeneratorTask(file=request.FILES['file'])
            instance = form.save()

            url_generator_task = UrlGeneratorTask.objects.get(id=instance.id)
            desc_list = give_me_rand_text_set(url_generator_task.description, url_generator_task.desc_variations*3)
            url_list = UrlGenerator.objects.filter(active=True)
            url_generator_task.results = u''
            url_generator_task.links_number = 0
            for my_url in url_list:
                if '!anc!' in str(my_url):
                    desc_temp = set(desc_list)
                    for i in range(url_generator_task.desc_variations):
                        tmp_url = str(my_url).replace('!key!', url_generator_task.youtube_key()).replace('!-key!', url_generator_task.youtube_key_reverse()).replace('!key|lowercase!', url_generator_task.youtube_key_lower()).replace('!anc!', desc_temp.pop())
                        url_generator_task.results += '<p><a target="_blank" href="' + tmp_url +'">' + tmp_url +'</a></p>'
                        url_generator_task.links_number += 1
                else:
                    tmp_url = str(my_url).replace('!key!', url_generator_task.youtube_key()).replace('!-key!', url_generator_task.youtube_key_reverse()).replace('!key|lowercase!', url_generator_task.youtube_key_lower())
                    url_generator_task.results += '<p><a target="_blank" href="' + tmp_url +'">' + tmp_url +'</a></p>'
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


'''

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['file']
        if form.is_valid():
            print(file.name)
            #print(file.url)
            print(file.size)
            print(file)
            file_url = default_storage.save(file.name, file)
            print (file_url)

            #save_path = os.path.join(settings.MEDIA_ROOT, settings.BACKBLAZEB2_BUCKET_NAME, 'uploads', file.name)
            #print(save_path)

            #default_storage = B2Storage()
            #path = default_storage.save(save_path, file)

            #filename = fs.upload_file(file.name, file)
            #uploaded_file_url = default_storage.path(path)
            #print(path)
            #handle_uploaded_file(request.FILES['file'])
            #handle_uploaded_file(request.FILES['file'])
            #large_file = open(request.FILES['file'], 'rb')
            #b2 = B2()
            #bucket = b2.buckets.get('VideoProjects')
            #myfile = file
            #if file.size <= 30000000:
            #    new_file = bucket.files.upload(contents=myfile, file_name='folder/'+file.name, content_length=file.size) #  content_length=content_length, progress_listener=progress_listener)
            #    print('Small file no threads')
            #elif file.size > 30000000:
            #    new_file = bucket.files.upload_large_file(contents=myfile, file_name='folder/' + file.name,
            #                                   content_length=file.size, num_threads=4)
            #    print('Large file 4 threads')


            #print(new_file.file_name, new_file.content_type, new_file.content_length, new_file.file_info)
            return HttpResponseRedirect('https://github.com/')
    else:
        form = UploadFileForm()
    return render(request, 'url_generator/upload.html', {'form': form})
'''

class ExampleFormView(generic.FormView):
    template_name = 'url_generator/upload.html'
    form_class = FileForm

    def get_success_url(self):
        return reverse('url_generator:upload_file')

    def form_valid(self, form):
        form.save()
        form.delete_temporary_files()
        return super(ExampleFormView, self).form_valid(form)




handle_upload = FileFormUploader()



'''
class ExampleView(generic.TemplateView, ChunkedFineUploader):
    template_name = 'url_generator/example.html'



class MyAppUploaderView(FineUploaderView):
    """FineUploaderView is basically a django.views.generic.FormView.
    So, you can use mixins or extends this view as you wish.
    You may want to see the code:
    django_fine_uploader.views.FineUploaderView
    Or you can create your own view, from scratch, and just take
    advantage from the upload handlers:
    django_fine_uploader.fineuploader.SimpleFineUploader
    OR
    django_fine_uploader.fineuploader.ChunkedFineUploader
    """
    # Do some stuff, override methods, change settings...


class NotConcurrentUploaderView(FineUploaderView):
    """Example of a chunked, but NOT concurrent upload.
    Disabling concurrent uploads per view.
    Remember, you can turn off concurrent uploads on your settings, with:
    FU_CONCURRENT_UPLOADS = False
    """
    @property
    def concurrent(self):
        return False

    def form_valid(self, form):
        self.process_upload(form)
        return self.make_response({'success': True})


class SimpleCustomUploaderView(generic.FormView):
    """Example of a not concurrent not chunked upload. A.K.A. Simple upload.
    """
    form_class = FineUploaderUploadForm

    def form_valid(self, form):
        """You could use the ChunkedFineUploader too, it will detect
        it's not a chunked upload, and it will upload anyway.
        from django_fine_uploader.fineuploader import ChunkedFineUploader
        upload = ChunkedFineUploader(form.cleaned_data, concurrent=False)
        ..but if you want a ~ real ~ simple upload:
        """
        upload = SimpleFineUploader(form.cleaned_data)
        upload.save()
        return JsonResponse({'success': True})

    def form_invalid(self, form):
        data = {'success': False, 'error': '%s' % repr(form.errors)}
        return JsonResponse(data, status=400)


class CustomFineUploaderView(FineUploaderView):
    """Let's get the file url and add to the json response, so we can
    get it on the frontend. More info on `onComplete` callback on
    myapp/example.html
    """
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CustomFineUploaderView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.process_upload(form)
        data = {'success': True}
        if self.upload.finished:
            data['file_url'] = self.upload.url
            # Let's save in database?
            FineFile.objects.create(fine_file=self.upload.real_path)
        return self.make_response(data)

'''