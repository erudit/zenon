# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-05 14:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0075_auto_20171005_0913"),
    ]

    operations = [
        migrations.RenameField(
            model_name="legacyorganisationprofile",
            old_name="sushi_requestor_id",
            new_name="sushi_requester_id",
        ),
    ]
