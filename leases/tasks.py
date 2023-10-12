
from utils.utils import logger as serverLogger
from celery.utils.log import get_task_logger

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Lease, Invoice, Bills

celeryLogger = get_task_logger(__name__)

@shared_task(name="create_recurring_invoices")
def create_monthly_invoices():
    celeryLogger.info("creating invoice...")
    # Get all active leases that are within their lease duration
    today = timezone.now().date()
    active_leases = Lease.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
    )

    celeryLogger.info(today.day)
    # Loop through active leases and create invoices
    for lease in active_leases:
        if today.day == lease.due_day:  # Check if today is the due day
            # Create a new invoice for this month
            next_month = today.replace(day=1) + timezone.timedelta(days=32)
            due_date = next_month.replace(day=lease.due_day)

            new_invoice = Invoice.objects.create(
                lease=lease,
                property=lease.property,
                unit=lease.unit,
                tenant=lease.tenant,
                total_amount=lease.rent,  # Use the rent amount from the lease
                due_on=due_date,
                status=Invoice.UNPAID,  # Set the initial payment status
                account=lease.account
            )
            new_invoice.save()

            bill = Bills.objects.create(
                invoice=new_invoice,
                item=_("Rent"),
                description=_(f"Rent payment for "),
                quantity=1,
                rate=lease.rent
            )
            bill.save()
            celeryLogger.info("invoice created...")










