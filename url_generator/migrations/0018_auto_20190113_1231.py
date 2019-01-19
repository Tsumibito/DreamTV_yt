# Generated by Django 2.1.1 on 2019-01-13 10:31

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('url_generator', '0017_urlgenerator_date_inactive'),
    ]

    operations = [
        migrations.CreateModel(
            name='StopDomains',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('domain', models.CharField(max_length=64, verbose_name='Domain name')),
            ],
        ),
        migrations.AlterModelManagers(
            name='urlgenerator',
            managers=[
                ('domains', django.db.models.manager.Manager()),
            ],
        ),
    ]
