# Generated by Django 3.2.9 on 2021-11-09 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0030_alter_strike_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='only_allow_prioritized',
            field=models.BooleanField(default=False),
        ),
    ]