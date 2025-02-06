# Generated by Django 4.2.4 on 2024-11-10 09:25

from django.db import migrations
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('leases', '0005_alter_lease_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
