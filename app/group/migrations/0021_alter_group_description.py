# Generated by Django 5.1.1 on 2024-12-26 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("group", "0020_alter_membership_membership_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
