from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("kontres", "0008_reservation_approved_by"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Reservation",
        ),
        migrations.DeleteModel(
            name="BookableItem",
        ),
    ]
