# Generated by Django 3.1.13 on 2021-10-02 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0003_sort_options_in_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='template',
            field=models.BooleanField(default=False),
        ),
    ]