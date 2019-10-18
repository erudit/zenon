# Generated by Django 2.0.13 on 2019-10-18 14:31

from django.db import migrations


def migrate_needs_correction_issue_submissions_status_tracks(apps, schema_editor):
    IssueSubmissionStatusTrack = apps.get_model('editor', 'IssueSubmissionStatusTrack')
    for status_track in IssueSubmissionStatusTrack.objects.filter(status='D'):
        status_track.status = 'C'
        status_track.save()


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0011_auto_20191018_0930'),
    ]

    operations = [
        migrations.RunPython(migrate_needs_correction_issue_submissions_status_tracks)
    ]
