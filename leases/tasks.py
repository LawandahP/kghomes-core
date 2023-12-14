from datetime import timedelta
from django.utils.dateformat import format
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Lease, Invoice, Bills
from celery import shared_task
from celery.utils.log import get_task_logger



celeryLogger = get_task_logger(__name__)

@shared_task(name="create_recurring_invoices")
def generate_monthly_invoice():
    '''
    This is a recurring function crontab which runs at a specific amount of
    time as set in config/celery.py
    It's designed to generate monthly invoices for leases with a rent frequency
    of 'Monthly', taking into account the due day specified in each lease. 
    Additionally, it ensures that a new invoice is generated/created only if 
    either the due day is two days from the current date or there is no existing 
    invoice for the current month and year.
    '''
    
    celeryLogger.info("creating invoice...")
    # get leases which have not expired
    today = timezone.now().date()
    active_leases = Lease.objects.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True)
    )
    
    for lease in active_leases:
        if lease.rent_frequency == 'Monthly':
            due_day = lease.due_day
            existing_invoice = Invoice.objects.filter(lease=lease, due_on__month=today.month, due_on__year=today.year).first()
            if (today + timedelta(days=5)).day == due_day and not existing_invoice or not existing_invoice:
                # if not existing_invoice:
                invoice = Invoice.objects.create(
                    lease=lease,
                    property=lease.property,
                    unit=lease.unit,
                    tenant=lease.tenant,
                    total_amount=lease.rent,
                    due_on=timezone.datetime(today.year, today.month, due_day).date(),
                    status="Unpaid",
                    account=lease.property.account
                )
                invoice.save()
                bill = Bills.objects.create(
                    invoice=invoice,
                    item="Rent",
                    description=f'Rent for {today.strftime("%B")}, {today.strftime("%Y")}',
                    quantity=1,
                    rate=lease.rent,
                )
                bill.save()
                celeryLogger.info("invoice created...")



@shared_task(name="update-invoice-status")
def updateInvoiceStatus():

    celeryLogger.info("updating invoice status...")
    today = timezone.now().date() 
    overdue_invoices = Invoice.objects.filter(due_on__lt=today, status__in=["Unpaid", "Due"])
    

    for invoice in overdue_invoices:
        if today > invoice.due_on:
            invoice.status = Invoice.OVERDUE
            invoice.save()
            celeryLogger.info("updated invoice status")
        else:
            pass





