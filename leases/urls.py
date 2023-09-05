from django.urls import path

from leases.views import CreatViewLease


urlpatterns = [
    path('leases/',  CreatViewLease.as_view(), name="images"),
]