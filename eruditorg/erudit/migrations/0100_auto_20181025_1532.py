# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-25 20:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0099_auto_20180925_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalinformation',
            name='instruction_for_authors',
            field=models.TextField(blank=True, null=True, verbose_name='Instructions pour les auteurs'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='instruction_for_authors_en',
            field=models.TextField(blank=True, null=True, verbose_name='Instructions pour les auteurs'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='instruction_for_authors_fr',
            field=models.TextField(blank=True, null=True, verbose_name='Instructions pour les auteurs'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='peer_review_process',
            field=models.CharField(blank=True, choices=[('SB', 'Simple aveugle'), ('DB', 'Double aveugle'), ('OR', 'Ouverte')], max_length=2, null=True, verbose_name='Type de processus d’évaluation par les pairs'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='publishing_ethics',
            field=models.TextField(blank=True, null=True, verbose_name='Politique anti-plagiat ou d’éthique'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='publishing_ethics_en',
            field=models.TextField(blank=True, null=True, verbose_name='Politique anti-plagiat ou d’éthique'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='publishing_ethics_fr',
            field=models.TextField(blank=True, null=True, verbose_name='Politique anti-plagiat ou d’éthique'),
        ),
    ]
