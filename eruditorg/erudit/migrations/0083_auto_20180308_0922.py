# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-08 14:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0082_auto_20180208_1331"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="is_published",
            field=models.BooleanField(default=False, verbose_name="Est publié sur www"),
        ),
    ]
