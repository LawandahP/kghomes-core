from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from files.models import Files, TimeStamps
from properties.models import Property
from units.models import Units

from utils.utils import CustomUUIDField, convertToMonth


current_date_time = datetime.now().date()
today = timezone.now().date()



TERMS = [
    ('Fixed Term', _('Fixed Term')),
    ('Month-To-Month', _('Month-To-Month')),
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

    ACTIVE = 'Active'
    EXPIRED = 'Expired'
    CANCELLED = 'Cancelled'
    BALANCE_DUE = 'Balance Due'
    
    LEASE_STATUS = [
        (ACTIVE, _(ACTIVE)),
        (EXPIRED, _(EXPIRED)),
        (CANCELLED, _(CANCELLED)),
        (BALANCE_DUE, _(BALANCE_DUE))
    ]

    id               = CustomUUIDField()
    property         = models.ForeignKey(Property, on_delete=models.CASCADE)
    unit             = models.ForeignKey(Units, on_delete=models.CASCADE)
    tenant           = models.CharField(max_length=100, null=True)
    term             = models.CharField(max_length=50, choices=TERMS, blank=True, null=True)
    rent             = models.IntegerField()
    first_rent_date  = models.DateField(blank=True, null=True)
    security_deposit = models.IntegerField(null=True, blank=True)
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



# create security deposit invoice
def create_deposit_invoice(instance):
    if instance.security_deposit is not None:
        deposit_description = f"Security Deposit for {instance.unit}"
        deposit_invoice = Invoice.objects.create(
            lease=instance,
            property=instance.property,
            unit=instance.unit,
            tenant=instance.tenant,
            total_amount=instance.security_deposit,
            due_on=instance.first_rent_date,  # Assuming the deposit is due on the lease start date
            account=instance.property.account,
        )

        # Set the deposit invoice status
        if instance.first_rent_date < today:
            deposit_invoice.status = Invoice.OVERDUE
        elif instance.first_rent_date == today:
            deposit_invoice.status = Invoice.DUE
        else:
            # If start date is in the future, leave status as Outstanding
            pass

        deposit_invoice.save()

        bill = Bills.objects.create(
            invoice=deposit_invoice,
            item="Deposit",
            description=deposit_description,
            quantity=1,
            rate=instance.security_deposit,
        )
        bill.save()
    else:
        pass

@receiver(post_save, sender=Lease)
def post_lease_signal(sender, instance, created, *args, **kwargs):
    if created:
        # If Lease is created create Invoice
        # prorate rent
        rent = instance.rent
        description = f'Rent for {convertToMonth(instance.first_rent_date)}'
        quantity = 1
        rate = rent

        if (instance.rent_frequency == 'Monthly' 
                and instance.first_rent_date.day > instance.due_day 
                and instance.first_rent_date.month == current_date_time.month 
                and instance.first_rent_date.year == current_date_time.year
            ):
            # Calculate prorated rent from first_rent_date to the end of the month
            if instance.first_rent_date.month == 12:
                next_month = instance.first_rent_date.replace(year=instance.first_rent_date.year + 1, month=1, day=1)
                end_of_month = instance.first_rent_date.replace(year=instance.first_rent_date.year + 1, month=1, day=1) - timezone.timedelta(days=1)
            else:
                next_month = instance.first_rent_date.replace(month=instance.first_rent_date.month + 1, day=1)
                end_of_month = instance.first_rent_date.replace(month=instance.first_rent_date.month + 1, day=1) - timezone.timedelta(days=1)

            days_in_month = (next_month - instance.first_rent_date.replace(day=1)).days
            days_to_charge = days_in_month - instance.first_rent_date.day + 1
            rent = (instance.rent / days_in_month) * days_to_charge
            rate = instance.rent / days_in_month
            quantity = days_to_charge
            description = f"Prorated Rent for {convertToMonth(instance.first_rent_date)} from {instance.first_rent_date.day} - {end_of_month.day}"
        
        elif instance.rent_frequency == 'Daily':
            # Daily rent is not prorated since it's charged per day
            rate = rent
            quantity = 1
            description = f"Daily Rent for {instance.first_rent_date.strftime('%Y-%m-%d')}"

        elif instance.rent_frequency == 'Weekly':
            # Calculate prorated rent from first_rent_date to the end of the week
            end_of_week = instance.first_rent_date + timedelta(days=(6 - instance.first_rent_date.weekday()))
            days_to_charge = (end_of_week - instance.first_rent_date).days + 1
            rent = (instance.rent / 7) * days_to_charge
            rate = instance.rent / 7
            quantity = days_to_charge
            description = f"Prorated Rent for week of {instance.first_rent_date.strftime('%Y-%m-%d')}"
        
        elif instance.rent_frequency == 'Every 2 Weeks':
            # Calculate prorated rent from first_rent_date to the end of the bi-weekly period
            end_of_period = instance.first_rent_date + timedelta(days=13)  # 2 weeks - 1 day
            days_to_charge = (end_of_period - instance.first_rent_date).days + 1
            rent = (instance.rent / 14) * days_to_charge
            rate = instance.rent / 14
            quantity = days_to_charge
            description = f"Prorated Rent for bi-weekly period starting {instance.first_rent_date.strftime('%Y-%m-%d')}"

        elif instance.rent_frequency == 'Quarterly':
            # Calculate prorated rent from first_rent_date to the end of the quarter
            # Assuming a quarter is 3 months
            months_to_charge = 3 - ((instance.first_rent_date.month - 1) % 3)
            rent = (instance.rent / 3) * months_to_charge
            rate = instance.rent / 3
            quantity = months_to_charge
            description = f"Prorated Rent for the quarter starting {instance.first_rent_date.strftime('%Y-%m-%d')}"

        elif instance.rent_frequency == 'Semi Annual':
            # Calculate prorated rent from first_rent_date to the end of the semi-annual period
            # Assuming a semi-annual period is 6 months
            months_to_charge = 6 - ((instance.first_rent_date.month - 1) % 6)
            rent = (instance.rent / 6) * months_to_charge
            rate = instance.rent / 6
            quantity = months_to_charge
            description = f"Prorated Rent for the semi-annual period starting {instance.first_rent_date.strftime('%Y-%m-%d')}"

        elif instance.rent_frequency == 'Annually':
            # Calculate prorated rent from first_rent_date to the end of the year
            end_of_year = datetime(instance.first_rent_date.year, 12, 31)
            days_to_charge = (end_of_year - instance.first_rent_date).days + 1
            rent = (instance.rent / 365) * days_to_charge
            rate = instance.rent / 365
            quantity = days_to_charge
            description = f"Prorated Rent for the year starting {instance.first_rent_date.strftime('%Y-%m-%d')}"
            
        invoice = Invoice.objects.create(
            lease=instance,
            property=instance.property,
            unit=instance.unit,
            tenant=instance.tenant,
            total_amount=rent,
            due_on=instance.first_rent_date,
            account=instance.property.account
        )

        # Check conditions and update invoice status                                   
        if instance.first_rent_date < today:
            # If first rent date has passed, set invoice status to Overdue
            invoice.status = Invoice.OVERDUE
        elif instance.first_rent_date == today:
            # If today is the first rent date, set invoice status to Due
            invoice.status = Invoice.DUE
        else:
            # If first rent date is in the future, leave status as Outstanding
            pass
        
        invoice.save()
        
        bill = Bills.objects.create(
            invoice=invoice,
            item="Rent",
            description=description,
            quantity=quantity,
            rate=rate,
        )
        bill.save()
        create_deposit_invoice(instance)




class Invoice(TimeStamps):
    PAID = 'Fully Paid'
    OUTSTANDING = 'Outstanding'
    PARTIAL = 'Partially Paid'
    OVERDUE = 'Overdue'
    DUE = 'Due'

    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Fully Paid'),
        (OUTSTANDING, 'Outstanding'),
        (PARTIAL, 'Partially Paid'),
        (DUE, 'DUE'),
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
    
    total_amount = models.IntegerField()
    due_on = models.DateField()

    amount_paid = models.IntegerField(blank=True, null=True)
    paid_on = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(blank=True, null=True, choices=PAYMENT_METHOD, max_length=255)
    balance = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES, default=OUTSTANDING)

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
    amount = models.IntegerField(null=True)

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

