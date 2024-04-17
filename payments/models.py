from datetime import datetime

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from files.models import TimeStamps
from leases.models import Invoice

current_date_time = datetime.now().date()

# Create your models here.
class Payment(TimeStamps):
    INVOICE = 'INVOICE'
    SUBSCRIPTION = 'INVOICE'
    SMS = 'SMS'

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Check', 'Check'),
        ('Mpesa', 'Mpesa'),
        ('Bank Transfer', 'Bank Transfer'),
    ]


    PAYMENT_FOR_CHOICES = [
        (INVOICE, 'INVOICE'),
        (SUBSCRIPTION, 'SUBSCRIPTION'),
        (SMS, 'SMS'),
    ]

    account = models.CharField(max_length=100)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, blank=True, null=True, related_name="invoicePayments")
    tenant = models.CharField(max_length=100, blank=True, null=True)    
    pay_for = models.CharField(max_length=100, choices=PAYMENT_FOR_CHOICES, default=INVOICE)    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_time = models.TimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="Cash")
    notes = models.TextField(blank=True, null=True)
    
    # Specific fields for different payment methods
    check_number = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)  # For both Check and Bank Transfer
    account_number = models.CharField(max_length=100, blank=True, null=True)  # Optional for Bank Transfer

    # for mpesa
    mpesa_receipt_number =  models.CharField(max_length=255, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    phonenumber = models.CharField(max_length=20, blank=True, null=True)  # For Mpesa

    def __str__(self):
        return f"Payment {self.id} by Tenant {self.tenant}"


    class Meta:
        db_table = 'payments'
        verbose_name_plural = 'Payments'




@receiver(post_save, sender=Payment)
def update_invoice_status(sender, instance, created, **kwargs):
    
    if created and instance.invoice:  # Check if there is a related invoice
        invoice = instance.invoice
        payment_amount = instance.amount_paid
        
        if invoice.amount_paid:
            paid_amount = instance.amount_paid + invoice.amount_paid
        else:
            paid_amount = instance.amount_paid

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
    
    else:
         # ? Find parent invoice and update total_amount
        invoice = instance.invoice
        payments_set = invoice.invoicePayments.all()
        sum = 0
        for payment in payments_set.iterator():
            sum += payment.amount_paid
            invoice.amount_paid = sum
            invoice.save()

            # ? Update invoice balance and status when payment is updated
            if invoice.balance == None:
                invoice.balance = 0
                # invoice.save()
            if invoice.balance > 0:
                invoice.balance = invoice.total_amount - invoice.amount_paid
                if invoice.total_amount != invoice.amount_paid:
                    invoice.status = "Partially Paid"
                elif invoice.total_amount != invoice.amount_paid:
                    invoice.status = "Fully Paid"
                    invoice.paid_on = current_date_time
                invoice.save()



@receiver(post_delete, sender=Payment)
def post_delete_payment_signal(sender, instance, *args, **kwargs):
    amount = instance.amount_paid
    invoice = instance.invoice
    if invoice.amount_paid:
        invoice.amount_paid = invoice.amount_paid - amount

        # update invoice balance
        invoice.balance = invoice.total_amount - invoice.amount_paid
        invoice.save()