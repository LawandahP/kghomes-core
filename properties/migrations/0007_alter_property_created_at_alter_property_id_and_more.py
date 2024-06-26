# Generated by Django 4.2.4 on 2024-04-02 20:44

import datetime
from django.db import migrations, models
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_alter_property_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 4, 2, 20, 44, 52, 730608, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='property',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='updated_at',
            field=models.DateField(auto_now=True, default=datetime.datetime(2024, 4, 2, 20, 44, 55, 66142, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
