# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-20 20:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0025_auto_20160714_1130"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="journal",
            name="next_code",
        ),
        migrations.RemoveField(
            model_name="journal",
            name="previous_code",
        ),
        migrations.AddField(
            model_name="journal",
            name="next_journal",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="+",
                to="erudit.Journal",
                verbose_name="Revue suivante",
            ),
        ),
        migrations.AddField(
            model_name="journal",
            name="previous_journal",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="+",
                to="erudit.Journal",
                verbose_name="Revue précédente",
            ),
        ),
    ]
