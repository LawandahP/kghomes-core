# Generated by Django 4.2.4 on 2024-05-15 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('leases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True, null=True)),
                ('account', models.CharField(max_length=100)),
                ('tenant', models.CharField(blank=True, max_length=100, null=True)),
                ('pay_for', models.CharField(choices=[('INVOICE', 'INVOICE'), ('INVOICE', 'SUBSCRIPTION'), ('SMS', 'SMS')], default='INVOICE', max_length=100)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField()),
                ('payment_time', models.TimeField(blank=True, null=True)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('Check', 'Check'), ('Mpesa', 'Mpesa'), ('Bank Transfer', 'Bank Transfer')], default='Cash', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('check_number', models.CharField(blank=True, max_length=100, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=100, null=True)),
                ('transaction_reference', models.CharField(blank=True, max_length=255, null=True)),
                ('account_number', models.CharField(blank=True, max_length=100, null=True)),
                ('mpesa_receipt_number', models.CharField(blank=True, max_length=255, null=True)),
                ('checkout_request_id', models.CharField(blank=True, max_length=255, null=True)),
                ('phonenumber', models.CharField(blank=True, max_length=20, null=True)),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoicePayments', to='leases.invoice')),
            ],
            options={
                'verbose_name_plural': 'Payments',
                'db_table': 'payments',
            },
        ),
    ]
