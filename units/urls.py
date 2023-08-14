from django.urls import path

from .views import CreatViewUnits

urlpatterns = [
    path('units/', CreatViewUnits.as_view(), name="create-units"),
    # path('properties/<str:slug>/', PropertyDetailView.as_view(),     name="property-detail"),
]
