# Generated by Django 4.2.5 on 2023-11-04 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0055_remove_qrcode_url_qrcode_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="created_by_admin",
            field=models.BooleanField(default=False),
        ),
    ]
