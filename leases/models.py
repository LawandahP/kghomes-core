from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver


from files.models import Files, TimeStamps
from properties.models import Property
from units.models import Units

from utils.utils import CustomUUIDField, convertToMonth


current_date_time = datetime.now().date()


ACTIVE = 'Active'
EXPIRED = 'Expired'

TERMS = [
    ('Fixed Term', _('Fixed Term')),
    ('Month-To-Month', _('Month-To-Month')),
]

LEASE_STATUS = [
    (ACTIVE, _('Active')),
    (EXPIRED, _('Expired'))
]

FREQUENCY = [
    ('Daily', _('Daily')),
    ('Weekly', _('Weekly')),
    ('Every 2 Weeks', _('Every 2 Weeks')),
    ('Monthly', _('Monthly')),
    ('Quarterly', _('Quarterly')),
    ('Semi Annual', _('Semi Annual')),
    ('Annually', _('Annually')),
]

# Create your models here.
class Lease(TimeStamps):
    id               = CustomUUIDField()
    property         = models.ForeignKey(Property, on_delete=models.CASCADE)
    unit             = models.ForeignKey(Units, on_delete=models.CASCADE)
    tenant           = models.CharField(max_length=100, null=True)
    term             = models.CharField(max_length=50, choices=TERMS, blank=True, null=True)
    rent             = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    first_rent_date  = models.DateField(blank=True, null=True)
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    rent_frequency   = models.CharField(max_length=50, choices=FREQUENCY)
    due_day          = models.IntegerField(null=True)
    start_date       = models.DateField(blank=True, null=True)
    end_date         = models.DateField(blank=True, null=True)
    file             = models.ForeignKey(Files, on_delete=models.CASCADE, null=True, blank=True)
    account          = models.CharField(max_length=50)
    status           = models.CharField(choices=LEASE_STATUS, default=ACTIVE)

    def __str__(self):
        return self.tenant

    class Meta:
        db_table = 'leases'
        verbose_name_plural = 'Leases'

@receiver(post_save, sender=Lease)
def post_lease_signal(sender, instance, created, *args, **kwargs):
    if created:
        # ? If Lease is first created create Invoice
        invoice = Invoice.objects.create(
            lease=instance,
            property=instance.property,
            unit=instance.unit,
            tenant=instance.tenant,
            total_amount=instance.rent,
            due_on=instance.first_rent_date,
            status=Invoice.UNPAID,
            account = instance.property.account
        )
        invoice.save()


        bill = Bills.objects.create(
            invoice=invoice,
            item="Rent",
            description=f'Rent for {convertToMonth(instance.first_rent_date)}',
            quantity=1,
            rate=instance.rent,
        )

        bill.save()


    

class Invoice(TimeStamps):
    PAID = 'Fully Paid'
    UNPAID = 'Unpaid'
    PARTIAL = 'Partially Paid'
    OVERDUE = 'Overdue'

    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Fully Paid'),
        (UNPAID, 'Unpaid'),
        (PARTIAL, 'Partially Paid'),
        (OVERDUE, 'Overdue')
    ]

    CHECK = 'Check'
    CASH = 'Cash'
    MPESA = 'Mpesa'
    BANK = 'Bank'

    PAYMENT_METHOD = [
        (CHECK, 'Check'),
        (CASH, 'Cash'),
        (MPESA, 'Mpesa'),
        (BANK, 'Bank')
    ]


    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='invoices')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    tenant = models.CharField(max_length=100, null=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_on = models.DateField()

    amount_paid = models.IntegerField(blank=True, null=True, default=0)
    paid_on = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(blank=True, null=True, choices=PAYMENT_METHOD, max_length=255)
    balance = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)

    account = models.CharField(max_length=50)

    def __str__(self):
        return self.tenant

    class Meta:
        db_table = 'invoices'
        verbose_name_plural = 'Invoices'



class Bills(TimeStamps):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoiceBills')
    item = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField()
    rate = models.IntegerField()
    amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.item

    class Meta:
        db_table = 'bills'
        verbose_name_plural = 'Bills'

@receiver(pre_save, sender=Bills)
def pre_bills_signal(sender, instance, *args, **kwargs):
    instance.amount = instance.rate * instance.quantity

@receiver(post_save, sender=Bills)
def post_bills_signal(sender, instance, created, *args, **kwargs):
    if created:
        # ? If bill is created update parent invoice total_amount
        amount = instance.amount
        
        invoice = instance.invoice

        if invoice.total_amount:
            invoice.total_amount = invoice.total_amount + int(amount)

        if invoice.total_amount and invoice.balance is not None:
            # invoice.total_amount = invoice.total_amount + int(amount)
            #? if invoice balance is > 1 add bill amount😎💸💸
            if invoice.balance is None:
                invoice.balance = 0
            if invoice.balance > 0:
                invoice.balance = invoice.balance + amount
            invoice.save()
        invoice.save()
    else:
        # ? Find parent invoice and update total_amount
        invoice = instance.invoice
        bills_set = invoice.invoiceBills.all()
        sum = 0
        for bill in bills_set.iterator():
            sum += bill.amount
            invoice.total_amount = sum
            invoice.save()

            # ? Update invoice balance and status when bill is updated
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


@receiver(post_delete, sender=Bills)
def post_delete_bills_signal(sender, instance, *args, **kwargs):
    amount = instance.amount
    invoice = instance.invoice
    if invoice.total_amount:
        invoice.total_amount = invoice.total_amount - amount
        if invoice.balance and invoice.balance > 0:
            invoice.balance = invoice.balance - amount
        invoice.save()

