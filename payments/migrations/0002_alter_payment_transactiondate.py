# Generated by Django 4.2.4 on 2024-02-04 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='TransactionDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
