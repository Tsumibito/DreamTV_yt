# Generated by Django 2.1.1 on 2019-01-20 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0030_auto_20190120_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchstack',
            name='s2',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='s2'),
        ),
    ]