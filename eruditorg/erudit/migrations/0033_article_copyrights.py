# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-10 15:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0032_auto_20160810_0756"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="copyrights",
            field=models.ManyToManyField(
                related_name="articles", to="erudit.Copyright", verbose_name="Droits d'auteurs"
            ),
        ),
    ]
