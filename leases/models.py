from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver


from files.models import Files, TimeStamps
from properties.models import Property
from units.models import Units

from utils.utils import CustomUUIDField, convertToMonth

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
            payment_status="Unpaid",
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
    PAID = 'Paid'
    UNPAID = 'Unpaid'
    PARTIAL = 'Partial'

    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
        (PARTIAL, 'Partial'),
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
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)

    account = models.CharField(max_length=50)

    def __str__(self):
        return self.tenant

    class Meta:
        db_table = 'invoices'
        verbose_name_plural = 'Invoices'



class Bills(TimeStamps):
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, related_name='invoiceBills', null=True)
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

