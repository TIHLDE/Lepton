# Generated by Django 4.2.5 on 2024-09-12 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("group", "0018_fine_defense"),
        ("content", "0065_merge_0060_minute_tag_0064_alter_userbio_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="minute",
            name="group",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="meeting_minutes",
                to="group.group",
            ),
        ),
    ]
