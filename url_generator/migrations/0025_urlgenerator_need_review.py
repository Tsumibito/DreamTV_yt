# Generated by Django 2.1.1 on 2019-01-17 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0024_auto_20190113_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlgenerator',
            name='need_review',
            field=models.BooleanField(default=False),
        ),
    ]
