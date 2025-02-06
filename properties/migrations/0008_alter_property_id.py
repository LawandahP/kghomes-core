# Generated by Django 4.2.4 on 2024-11-12 16:17

from django.db import migrations
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0007_category_propertyamenities_alter_property_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
