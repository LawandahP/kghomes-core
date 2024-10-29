# Generated by Django 4.2.4 on 2024-05-15 11:45

from django.db import migrations, models
import utils.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Files',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True, null=True)),
                ('id', utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('file_url', models.FileField(blank=True, null=True, upload_to='files')),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Files',
                'db_table': 'files',
            },
        ),
    ]
