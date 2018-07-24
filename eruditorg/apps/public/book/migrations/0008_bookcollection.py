# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-18 00:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0007_auto_20180717_1934'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_name', models.CharField(max_length=200, verbose_name='Titre de collection')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Logo de collection')),
                ('description', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Description de la collection')),
            ],
        ),
    ]