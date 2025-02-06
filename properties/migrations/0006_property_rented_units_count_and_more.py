# Generated by Django 4.2.4 on 2024-11-10 09:25

from django.db import migrations, models
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_property_has_units_alter_property_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='rented_units_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='vacant_units_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
