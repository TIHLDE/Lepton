# Generated by Django 4.2.5 on 2024-04-06 09:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("kontres", "0007_bookableitem_image_bookableitem_image_alt"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_reservations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]