# Generated by Django 2.1.1 on 2019-01-13 13:01

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0019_auto_20190113_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchUrlStack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=256, verbose_name='URL')),
            ],
        ),
        migrations.AlterModelManagers(
            name='stopdomain',
            managers=[
                ('domains', django.db.models.manager.Manager()),
            ],
        ),
    ]
