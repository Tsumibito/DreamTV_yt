# Generated by Django 2.1.1 on 2019-01-17 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0025_urlgenerator_need_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchurlstack',
            name='domain',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Domain name'),
        ),
    ]