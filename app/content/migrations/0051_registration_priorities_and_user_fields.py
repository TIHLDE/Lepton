# Generated by Django 4.0.4 on 2022-05-08 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0050_alter_user_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='registration_priorities',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_class',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_study',
        ),
        migrations.DeleteModel(
            name='Priority',
        ),
    ]
