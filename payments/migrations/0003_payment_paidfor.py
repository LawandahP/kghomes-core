# Generated by Django 4.2.4 on 2024-02-11 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_payment_transactiondate'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='PaidFor',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
