# Generated by Django 3.1.8 on 2021-04-19 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0021_strike'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_TIHLDE_member',
        ),
    ]