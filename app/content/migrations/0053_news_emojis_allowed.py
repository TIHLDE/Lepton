# Generated by Django 4.0.8 on 2023-09-26 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0052_event_rules_and_photo_in_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='emojis_allowed',
            field=models.BooleanField(default=False),
        ),
    ]