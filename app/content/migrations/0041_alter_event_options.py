# Generated by Django 3.2.10 on 2022-02-25 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0040_move_badge_and_user_badge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ('start_date',)},
        ),
    ]
