# Generated by Django 4.2.4 on 2024-02-04 17:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('leases', '0004_alter_invoice_status_alter_lease_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('updated_at', models.DateField(blank=True, null=True)),
                ('account', models.CharField(max_length=100)),
                ('PayFor', models.CharField(choices=[('INVOICE', 'INVOICE'), ('INVOICE', 'SUBSCRIPTION'), ('SMS', 'SMS')], default='INVOICE', max_length=100)),
                ('PhoneNumber', models.CharField(blank=True, max_length=20, null=True)),
                ('MpesaReceiptNumber', models.CharField(max_length=255)),
                ('Amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('CheckoutRequestID', models.CharField(blank=True, max_length=255, null=True)),
                ('TransactionDate', models.DateTimeField()),
                ('Invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leases.invoice')),
            ],
            options={
                'verbose_name_plural': 'Payments',
                'db_table': 'payments',
            },
        ),
    ]
