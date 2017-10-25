# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-05 14:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0074_journal_is_new'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyOrganisationProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=10, verbose_name='Identifiant')),
                ('sushi_requestor_id', models.CharField(max_length=10, verbose_name='Identifiant SUSHI')),
                ('organisation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='erudit.Organisation')),
            ],
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='contact',
            field=models.TextField(blank=True, null=True, verbose_name='Coordonnées'),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='contact_en',
            field=models.TextField(blank=True, null=True, verbose_name='Coordonnées'),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='contact_fr',
            field=models.TextField(blank=True, null=True, verbose_name='Coordonnées'),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='editorial_policy',
            field=models.TextField(blank=True, null=True, verbose_name='Politiques de la revue'),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='editorial_policy_en',
            field=models.TextField(blank=True, null=True, verbose_name='Politiques de la revue'),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='editorial_policy_fr',
            field=models.TextField(blank=True, null=True, verbose_name='Politiques de la revue'),
        ),
    ]
