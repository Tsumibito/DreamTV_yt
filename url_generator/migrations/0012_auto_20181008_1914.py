# Generated by Django 2.1.1 on 2018-10-08 16:14

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0011_finefile'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LoadFileData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_file', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/Users/mymac/PycharmProjects/DreamTV_world/files/media'), upload_to='example')),
                ('load_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='url_generator.LoadFile')),
            ],
        ),
        migrations.DeleteModel(
            name='FineFile',
        ),
    ]
