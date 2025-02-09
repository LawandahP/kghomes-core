# Generated by Django 4.2.4 on 2024-05-15 11:45

from django.db import migrations, models
import django.db.models.deletion
import utils.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('files', '0001_initial'),
        ('properties', '0001_initial'),
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('account', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Line Items',
                'db_table': 'lineitems',
            },
        ),
        migrations.CreateModel(
            name='Lease',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True, null=True)),
                ('id', utils.utils.CustomUUIDField(default=utils.utils.CustomUUIDField.generate_uuid, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('tenant', models.CharField(max_length=100, null=True)),
                ('term', models.CharField(blank=True, choices=[('Fixed Term', 'Fixed Term'), ('Month-To-Month', 'Month-To-Month')], max_length=50, null=True)),
                ('rent', models.IntegerField()),
                ('first_rent_date', models.DateField(blank=True, null=True)),
                ('security_deposit', models.IntegerField(blank=True, null=True)),
                ('rent_frequency', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Every 2 Weeks', 'Every 2 Weeks'), ('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), ('Semi Annual', 'Semi Annual'), ('Annually', 'Annually')], max_length=50)),
                ('due_day', models.IntegerField(null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('account', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Cancelled', 'Cancelled'), ('Balance Due', 'Balance Due')], default='Active', max_length=255)),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='files.files')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='properties.property')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='units.units')),
            ],
            options={
                'verbose_name_plural': 'Leases',
                'db_table': 'leases',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True, null=True)),
                ('tenant', models.CharField(max_length=100, null=True)),
                ('total_amount', models.IntegerField()),
                ('due_on', models.DateField()),
                ('amount_paid', models.IntegerField(blank=True, null=True)),
                ('paid_on', models.DateTimeField(blank=True, null=True)),
                ('payment_method', models.CharField(blank=True, choices=[('Check', 'Check'), ('Cash', 'Cash'), ('Mpesa', 'Mpesa'), ('Bank', 'Bank')], max_length=255, null=True)),
                ('balance', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Fully Paid', 'Fully Paid'), ('Outstanding', 'Outstanding'), ('Partially Paid', 'Partially Paid'), ('Due', 'DUE'), ('Overdue', 'Overdue')], default='Outstanding', max_length=100)),
                ('account', models.CharField(max_length=50)),
                ('lease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='leases.lease')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='properties.property')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='units.units')),
            ],
            options={
                'verbose_name_plural': 'Invoices',
                'db_table': 'invoices',
            },
        ),
        migrations.CreateModel(
            name='Bills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('quantity', models.IntegerField()),
                ('rate', models.IntegerField()),
                ('amount', models.IntegerField(null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoiceBills', to='leases.invoice')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leases.lineitem')),
            ],
            options={
                'verbose_name_plural': 'Bills',
                'db_table': 'bills',
            },
        ),
    ]
