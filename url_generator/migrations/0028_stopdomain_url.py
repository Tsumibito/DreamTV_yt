# Generated by Django 2.1.1 on 2019-01-19 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0027_searchurlstack_attempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='stopdomain',
            name='url',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Url that where baned'),
        ),
    ]
