# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-24 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0011_auto_20180723_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='contributors',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Contributeurs'),
        ),
    ]