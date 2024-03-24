from datetime import timedelta
from django.utils.dateformat import format
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Lease, Invoice, Bills, LineItem
from celery import shared_task
from celery.utils.log import get_task_logger



celeryLogger = get_task_logger(__name__)
today = timezone.now().date() 

@shared_task(name="create_recurring_invoices")
def generate_invoices():
    '''
    This function generates invoices for leases with different rent frequencies.
    It ensures that a new invoice is generated/created only if there is no existing 
    invoice for the current period.
    '''
    
    celeryLogger.info("creating invoice...")
    active_leases = Lease.objects.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True)
    )
    
    for lease in active_leases:
        existing_invoice = Invoice.objects.filter(
            lease=lease, 
            due_on__year=today.year,
            due_on__month=today.month,
            due_on__day=today.day if lease.rent_frequency == 'Daily' else None
        ).first()

        if not existing_invoice:
            # continue

            if lease.rent_frequency == 'Monthly':
                due_date = timezone.datetime(today.year, today.month, lease.due_day).date()
                if (today + timedelta(days=5)).day != lease.due_day:
                    continue
            elif lease.rent_frequency == 'Every 2 Weeks':
                # Assuming the lease started on a Friday, calculate the next due date that falls on a Friday
                due_date = today + timedelta(days=(4 - today.weekday()) % 7)
                while due_date <= today or (due_date - lease.start_date).days % 14 != 0:
                    due_date += timedelta(weeks=2)
            elif lease.rent_frequency == 'Quarterly':
                # Find the first day of the next quarter
                quarter_starts = [timezone.datetime(today.year, month, 1).date() for month in [1, 4, 7, 10]]
                due_date = next((date for date in quarter_starts if date > today), None)
                if due_date is None:  # If we're in the last quarter, move to the next year
                    due_date = timezone.datetime(today.year + 1, 1, 1).date()
            elif lease.rent_frequency == 'Weekly':
                # Assuming the lease started on a Friday, calculate the next due date that falls on a Friday
                due_date = today + timedelta(days=(4 - today.weekday()) % 7)
                while due_date <= today:
                    due_date += timedelta(weeks=1)
            elif lease.rent_frequency == 'Daily':
                due_date = today
            else:
                continue

            invoice = Invoice.objects.create(
                lease=lease,
                property=lease.property,
                unit=lease.unit,
                tenant=lease.tenant,
                total_amount=lease.rent,
                due_on=due_date,
                status=Invoice.OUTSTANDING,
                account=lease.property.account
            )
            invoice.save()

            line_item, created = LineItem.objects.get_or_create(name="Rent", account=lease.property.account)
            bill = Bills.objects.create(
                invoice=invoice,
                item=line_item,
                description=f"{lease.rent_frequency} Rent for {due_date.strftime('%d')  if lease.rent_frequency == 'Daily' else ''} {due_date.strftime('%B')}, {due_date.strftime('%Y')}",
                quantity=1,
                rate=lease.rent,
            )
            bill.save()
            celeryLogger.info(f"invoice created...month {today.month} day{today.day} year{today.year}")




@shared_task(name="update-invoice-status")
def updateInvoiceStatus():
    celeryLogger.info("Updating invoice status...")
    invoices = Invoice.objects.filter(due_on__lte=today, status__in=["Outstanding", "Due"])

    for invoice in invoices:
        if today > invoice.due_on:
            invoice.status = Invoice.OVERDUE
        elif today == invoice.due_on:
            invoice.status = Invoice.DUE
        invoice.save()
        celeryLogger.info(f"updated invoice status to {invoice.status}")


@shared_task(name="update-lease-status")
def updateLeaseStatus():
    celeryLogger.info("Updating lease status...")
    leases = Lease.objects.all()
    
    for lease in leases:
        if lease.end_date and lease.end_date < today:
            lease.status = Lease.EXPIRED
        else:
            all_invoices_paid = all(invoice.status == Invoice.PAID for invoice in lease.invoices.all())
            if all_invoices_paid:
                lease.status = Lease.ACTIVE
            else:
                lease.status = Lease.BALANCE_DUE

        lease.save()


