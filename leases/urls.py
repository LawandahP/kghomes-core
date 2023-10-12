from django.urls import path

from leases.views import (
    CreatViewLease, LeaseDetailView, 
    CreateInvoiceView, InvoiceDetailView,
    BillsCreateListView, BillDetailView
)


urlpatterns = [
    path('leases/',  CreatViewLease.as_view(), name="leases"),
    path('lease-details/<str:id>', LeaseDetailView.as_view(), name="lease_details"),

    path('invoices/',  CreateInvoiceView.as_view(), name="invoices"),
    path('invoice/<int:id>', InvoiceDetailView.as_view(), name="invoices-detail"),

    path('bills/',  BillsCreateListView.as_view(), name="bills"),
    path('bills/<int:id>', BillDetailView.as_view(), name="bills-detail")   
]