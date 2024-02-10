from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from files.models import TimeStamps
from leases.models import Invoice

# Create your models here.
class Payment(TimeStamps):
    INVOICE = 'INVOICE'
    SUBSCRIPTION = 'INVOICE'
    SMS = 'SMS'


    PAYMENT_FOR_CHOICES = [
        (INVOICE, 'INVOICE'),
        (SUBSCRIPTION, 'SUBSCRIPTION'),
        (SMS, 'SMS'),
    ]

    account = models.CharField(max_length=100)
    PayFor = models.CharField(max_length=100, choices=PAYMENT_FOR_CHOICES, default=INVOICE)
    Invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, blank=True, null=True)
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True)
    MpesaReceiptNumber = models.CharField(max_length=255)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    CheckoutRequestID = models.CharField(max_length=255, blank=True, null=True)
    TransactionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.PhoneNumber

    class Meta:
        db_table = 'payments'
        verbose_name_plural = 'Payments'




@receiver(post_save, sender=Payment)
def update_invoice_status(sender, instance, created,**kwargs):
    
    if created and instance.Invoice:  # Check if there is a related invoice
        invoice = instance.Invoice
        
        if invoice.amount_paid:
            paid_amount = instance.Amount + invoice.amount_paid
        else:
            paid_amount = instance.Amount

        invoice_amount = invoice.total_amount  

        # Subtract the paid amount from the invoice's total amount
        balance = invoice_amount - paid_amount  # Assuming your Invoice model has an 'amount' field

        if paid_amount < invoice_amount:
            invoice.status = Invoice.PARTIAL
        elif balance == 0:
            invoice.status = Invoice.PAID
        else:  # paid_amount > invoice_amount
            invoice.status = 'Overpaid'

        invoice.amount_paid = paid_amount
        invoice.balance = balance
        invoice.save()  # save the invoice after updating

