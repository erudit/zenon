# Generated by Django 2.0.13 on 2019-05-01 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0113_auto_20190328_1450'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journal',
            name='publishers',
        ),
        migrations.DeleteModel(
            name='Publisher',
        ),
    ]