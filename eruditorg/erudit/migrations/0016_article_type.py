# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-17 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0015_auto_20160614_1310"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="type",
            field=models.CharField(
                choices=[
                    ("article", "Article"),
                    ("compterendu", "Compte-rendu"),
                    ("autre", "Autre"),
                ],
                default="article",
                max_length=64,
                verbose_name="Type",
            ),
            preserve_default=False,
        ),
    ]
