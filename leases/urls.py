from django.urls import path

from leases.views import (
    LeaseViewSet, 
    CreateInvoiceView, InvoiceDetailView,
    BillsCreateListView, BillDetailView,
    LineItemViewSet
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'line-items', LineItemViewSet)
router.register(r'leases', LeaseViewSet, basename="leases")


urlpatterns = [
    path('invoices/',  CreateInvoiceView.as_view(), name="invoices"),
    path('invoice/<int:id>', InvoiceDetailView.as_view(), name="invoices-detail"),

    path('bills/',  BillsCreateListView.as_view(), name="bills"),
    path('bills/<int:id>', BillDetailView.as_view(), name="bills-detail"),
    
    path('', include(router.urls)), 
]