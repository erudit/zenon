# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-04 13:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0071_remove_journal_upcoming'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='publisher',
        ),
    ]