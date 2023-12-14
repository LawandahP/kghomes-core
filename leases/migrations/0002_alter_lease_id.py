# Generated by Django 4.2.4 on 2023-11-30 12:24

from django.db import migrations
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('leases', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
