# Generated by Django 3.0.14 on 2021-05-27 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0127_remove_journalinformation_languages'),
    ]

    operations = [
        migrations.AddField(
            model_name='discipline',
            name='type',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='erudit.JournalType', verbose_name='Type'),
            preserve_default=False,
        ),
    ]
