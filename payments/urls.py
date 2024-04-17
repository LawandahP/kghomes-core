from django.urls import path
from .views import PaymentListCreate, PaymentDetailView

urlpatterns = [
    path('payment/', PaymentListCreate.as_view(), name='payment-list-create'),
    path('payment/<int:id>', PaymentDetailView.as_view(), name='payment-details'),
]