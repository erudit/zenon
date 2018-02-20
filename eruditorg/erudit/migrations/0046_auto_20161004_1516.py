# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-04 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0045_auto_20161004_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuecontributor',
            name='role_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Rôle du contributeur'),
        ),
        migrations.AlterField(
            model_name='issuecontributor',
            name='role_name_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Rôle du contributeur'),
        ),
        migrations.AlterField(
            model_name='issuecontributor',
            name='role_name_fr',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Rôle du contributeur'),
        ),
    ]