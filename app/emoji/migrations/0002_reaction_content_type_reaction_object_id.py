# Generated by Django 4.0.8 on 2023-09-26 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('emoji', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reaction',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='reaction',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]