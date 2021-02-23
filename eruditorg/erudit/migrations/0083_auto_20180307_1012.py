# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-07 15:12
from __future__ import unicode_literals

from django.db import migrations, models


def set_journaltypes(apps, schema_editor):
    JournalType = apps.get_model("erudit", "JournalType")
    NAMES = [
        ("C", "Culturelle", "Cultural"),
        ("S", "Savante", "Scholarly"),
    ]
    for code, name_fr, name_en in NAMES:
        jt, _ = JournalType.objects.get_or_create(code=code)
        jt.name_fr = name_fr
        jt.name_en = name_en
        jt.save()


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0082_auto_20180208_1331"),
    ]

    operations = [
        migrations.AddField(
            model_name="journaltype",
            name="name_en",
            field=models.CharField(max_length=255, null=True, verbose_name="Nom"),
        ),
        migrations.AddField(
            model_name="journaltype",
            name="name_fr",
            field=models.CharField(max_length=255, null=True, verbose_name="Nom"),
        ),
        migrations.RunPython(set_journaltypes),
    ]
