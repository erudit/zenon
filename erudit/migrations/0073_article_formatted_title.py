# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-05 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0072_remove_article_publisher'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='formatted_title',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
