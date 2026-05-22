from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0068_alter_cheatsheet_grade_alter_cheatsheet_study_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Minute",
        ),
    ]
