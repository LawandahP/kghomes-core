# Generated by Django 4.2.4 on 2024-03-21 17:53

from django.db import migrations
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0014_alter_property_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
