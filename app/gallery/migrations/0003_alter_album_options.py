# Generated by Django 4.2.5 on 2024-10-21 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0002_remove_picture_album_album_id_alter_album_slug"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="album",
            options={"ordering": ["-created_at"]},
        ),
    ]
