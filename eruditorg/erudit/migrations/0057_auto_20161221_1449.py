# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-21 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0056_auto_20161111_1125"),
    ]

    operations = [
        migrations.AlterField(
            model_name="journaltype",
            name="name",
            field=models.CharField(default="N", max_length=255, verbose_name="Nom"),
            preserve_default=False,
        ),
    ]
