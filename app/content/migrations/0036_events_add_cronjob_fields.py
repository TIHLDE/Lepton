# Generated by Django 3.2.10 on 2022-01-22 10:58

from django.db import migrations, models
from django.utils.timezone import now

def set_runned_booleans(apps, schema_editor):
    Event = apps.get_model('content', 'Event')
    for event in Event.objects.all():
        event.runned_post_event_actions = now() > event.end_date
        event.runned_sign_off_deadline_reminder = now() > event.sign_off_deadline
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0035_auto_20211114_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='end_date_schedular_id',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sign_off_deadline_schedular_id',
        ),
        migrations.AddField(
            model_name='event',
            name='runned_post_event_actions',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='runned_sign_off_deadline_reminder',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_runned_booleans, migrations.RunPython.noop),
    ]