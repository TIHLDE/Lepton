# Generated by Django 3.2.10 on 2022-02-06 11:07

from django.db import migrations

from app.util.migrations import UpdateContentType


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0039_remove_user_cell'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='userbadge',
                    name='badge',
                ),
                migrations.RemoveField(
                    model_name='userbadge',
                    name='user',
                ),
                migrations.DeleteModel(
                    name='UserBadge',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name='UserBadge',
                    table='badge_userbadge',
                ),
                UpdateContentType(app='content', model='userbadge', new_app='badge'),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                   name='Badge',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                   name='Badge',
                   table='badge_badge',
                ),
                UpdateContentType(app='content', model='badge', new_app='badge'),
            ],
        ),
    ]