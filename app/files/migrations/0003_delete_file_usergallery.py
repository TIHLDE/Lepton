from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("files", "0002_remove_file_url_file_file"),
    ]

    operations = [
        migrations.DeleteModel(
            name="File",
        ),
        migrations.DeleteModel(
            name="UserGallery",
        ),
    ]
