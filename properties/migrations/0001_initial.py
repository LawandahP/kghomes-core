# Generated by Django 4.2.4 on 2023-08-08 21:29

from django.db import migrations, models
import utils.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.JSONField(blank=True, null=True)),
                ('latlng', models.JSONField(blank=True, null=True)),
                ('bounds', models.JSONField(blank=True, null=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('property_type', models.CharField(blank=True, max_length=100, null=True)),
                ('amenities', models.JSONField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('owner', models.JSONField(blank=True, null=True)),
                ('account', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Properties',
                'db_table': 'properties',
            },
        ),
    ]
