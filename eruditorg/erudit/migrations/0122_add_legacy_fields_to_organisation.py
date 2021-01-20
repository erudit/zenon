# Generated by Django 3.0.11 on 2021-01-20 16:28

from django.db import migrations, models


def add_default_account_id_and_sushi_requester_id(apps, schemaeditor):
    LegacyOrganisationProfile = apps.get_model('erudit', 'LegacyOrganisationProfile')

    for lop in LegacyOrganisationProfile.objects.all().prefetch_related('organisation'):
        lop.organisation.account_id = lop.account_id
        lop.organisation.sushi_requester_id = lop.sushi_requester_id
        lop.organisation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0121_remove_organisation_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='account_id',
            field=models.CharField(default='', max_length=10, verbose_name='Identifiant'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organisation',
            name='sushi_requester_id',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Identifiant SUSHI'),
        ),
        migrations.RunPython(add_default_account_id_and_sushi_requester_id)
    ]
