# Generated by Django 4.0.8 on 2023-02-06 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emoji', '0002_alter_usernewsreaction_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usernewsreaction',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='usernewsreaction',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='usernewsreaction',
            constraint=models.UniqueConstraint(fields=('user', 'news'), name='unique together: user and news'),
        ),
    ]