# Generated by Django 4.2.4 on 2024-02-04 21:11

from django.db import migrations
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0004_alter_assignment_id_alter_units_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='units',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
