# Generated by Django 3.2.3 on 2021-06-01 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0023_auto_20210601_1836'),
    ]

    operations = [
        migrations.DeleteModel(
            name='InstitutionReferer',
        ),
    ]