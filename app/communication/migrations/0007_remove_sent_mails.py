from django.db import migrations


def delete_sent(apps, schema_editor):
    Mail = apps.get_model("communication", "Mail")
    Mail.objects.filter(sent=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("communication", "0006_alter_mail_users"),
    ]

    operations = [
        migrations.RunPython(delete_sent),
        migrations.RemoveField(
            model_name="mail",
            name="sent",
        ),
    ]
