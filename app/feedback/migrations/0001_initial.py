# Generated by Django 4.2.16 on 2024-10-11 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        default="OPEN",
                        max_length=20,
                        verbose_name=[
                            ("OPEN", "Åpen"),
                            ("CLOSED", "Lukket"),
                            ("IN_PROGRESS", "Under arbeid"),
                            ("REJECTED", "Avvist"),
                        ],
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "ordering": ("created_at",),
            },
        ),
        migrations.CreateModel(
            name="Bug",
            fields=[
                (
                    "feedback_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="feedback.feedback",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("feedback.feedback",),
        ),
        migrations.CreateModel(
            name="Idea",
            fields=[
                (
                    "feedback_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="feedback.feedback",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("feedback.feedback",),
        ),
    ]
