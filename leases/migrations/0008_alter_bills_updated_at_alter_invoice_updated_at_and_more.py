# Generated by Django 4.2.4 on 2024-04-03 07:44

from django.db import migrations, models
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('leases', '0007_alter_bills_created_at_alter_bills_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bills',
            name='updated_at',
            field=models.DateField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='updated_at',
            field=models.DateField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='lease',
            name='id',
            field=utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='lease',
            name='updated_at',
            field=models.DateField(auto_now=True, null=True),
        ),
    ]
