# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-09 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0040_article_external_pdf_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="journal",
            name="redirect_to_external_url",
            field=models.BooleanField(
                default=True,
                help_text="Cocher si les numéros de cette revue ne sont pas hébergés sur la plateforme Érudit",
                verbose_name="Rediriger vers l'URL externe",
            ),
        ),
    ]
