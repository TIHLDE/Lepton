# Generated by Django 3.2.8 on 2021-11-16 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0009_alter_group_options'),
        ('forms', '0006_added_field_and_options_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupForm',
            fields=[
                ('form_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='forms.form')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forms', to='group.group')),
            ],
            options={
                'verbose_name': 'Group form',
                'verbose_name_plural': 'Group forms',
            },
            bases=('forms.form',),
        ),
    ]