# Generated by Django 3.2.8 on 2021-10-19 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0028_enforce_strikes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='priority',
        ),
    ]
