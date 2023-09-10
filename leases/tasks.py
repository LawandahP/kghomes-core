
from utils.utils import logger as serverLogger
from celery.utils.log import get_task_logger

# celeryLogger = get_task_logger(__name__)

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Lease, Invoice, Bills

@shared_task
def create_monthly_invoices():
    # Get all active leases that are within their lease duration
    today = timezone.now().date()
    active_leases = Lease.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
    )

    # Loop through active leases and create invoices
    for lease in active_leases:
        if today.day == lease.due_day:  # Check if today is the due day
            # Create a new invoice for this month
            next_month = today.replace(day=1) + timezone.timedelta(days=32)
            due_date = next_month.replace(day=lease.due_day)
            new_invoice = Invoice.objects.create(
                lease=lease,
                invoice_date=today,
                due_date=due_date,
                total_amount=lease.rent,  # Use the rent amount from the lease
                payment_status=Invoice.UNPAID,  # Set the initial payment status
            )
            rent_bill = Bills.objects.create(
                lease=lease,
                invoice=new_invoice,
                item=_("Rent"),
                description=_(f"Rent payment for ")
                
            )










