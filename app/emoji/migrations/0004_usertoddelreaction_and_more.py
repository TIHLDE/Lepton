# Generated by Django 4.0.8 on 2023-02-13 16:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0052_event_rules_and_photo_in_user'),
        ('emoji', '0003_alter_usernewsreaction_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToddelReaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('emoji', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='emoji.customemoji')),
                ('toddel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.toddel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='usertoddelreaction',
            constraint=models.UniqueConstraint(fields=('user', 'toddel'), name='unique together: user and toddel'),
        ),
    ]