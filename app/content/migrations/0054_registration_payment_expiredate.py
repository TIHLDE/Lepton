# Generated by Django 4.2.5 on 2023-10-18 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0053_event_contact_person"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="payment_expiredate",
            field=models.DateTimeField(default=None, null=True),
        ),
    ]