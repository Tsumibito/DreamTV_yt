# Generated by Django 2.1.1 on 2018-10-01 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UrlGenerator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=512)),
                ('anc', models.BooleanField(default=False)),
                ('stoped', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UrlGeneratorTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('youtube_url', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('desc_variations', models.PositiveSmallIntegerField(blank=True, default='1', null=True)),
                ('results', models.TextField(blank=True, null=True)),
                ('errors', models.TextField(blank=True, null=True)),
            ],
        ),
    ]