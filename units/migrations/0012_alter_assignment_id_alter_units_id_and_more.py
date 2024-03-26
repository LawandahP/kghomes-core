# Generated by Django 4.2.4 on 2024-02-11 18:34

from django.db import migrations, models
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0011_alter_assignment_id_alter_units_id'),
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
        migrations.AlterField(
            model_name='units',
            name='unit_type',
            field=models.CharField(blank=True, choices=[('Apartment', 'Apartment'), ('Studio', 'Studio'), ('Single Room', 'Single Room'), ('Shop', 'Shop'), ('Office', 'Office'), ('Warehouse', 'Warehouse'), ('Garage', 'Garage'), ('Restaurant', 'Restaurant'), ('Clinic', 'Clinic')], max_length=50, null=True),
        ),
    ]