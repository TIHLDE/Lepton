# Generated by Django 4.2.5 on 2023-10-04 08:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("communication", "0007_remove_sent_mails"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="banner",
            options={"ordering": ("-visible_from",)},
        ),
    ]