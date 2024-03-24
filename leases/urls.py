from django.urls import path

from leases.views import (
    CreatViewLease, LeaseDetailView, 
    CreateInvoiceView, InvoiceDetailView,
    BillsCreateListView, BillDetailView,
    LineItemViewSet
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'line-items', LineItemViewSet)


urlpatterns = [
    path('leases/',  CreatViewLease.as_view(), name="leases"),
    path('lease-details/<str:id>', LeaseDetailView.as_view(), name="lease_details"),

    path('invoices/',  CreateInvoiceView.as_view(), name="invoices"),
    path('invoice/<int:id>', InvoiceDetailView.as_view(), name="invoices-detail"),

    path('bills/',  BillsCreateListView.as_view(), name="bills"),
    path('bills/<int:id>', BillDetailView.as_view(), name="bills-detail"),
    
    path('', include(router.urls)), 
]