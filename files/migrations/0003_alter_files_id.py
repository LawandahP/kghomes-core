# Generated by Django 4.2.4 on 2024-11-03 11:11

from django.db import migrations
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_alter_files_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
