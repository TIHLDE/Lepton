from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("codex", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CodexEventRegistration",
        ),
        migrations.DeleteModel(
            name="CodexEvent",
        ),
    ]
