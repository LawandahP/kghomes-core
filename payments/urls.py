from django.urls import path
from .views import PaymentListCreate

urlpatterns = [
    path('payment/', PaymentListCreate.as_view(), name='payment-list-create'),
]