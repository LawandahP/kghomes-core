from django.urls import path

from .views import CreatViewUnits, AssignUnitToTenant, UnitDetailView

urlpatterns = [
    path('units/', CreatViewUnits.as_view(), name="create-units"),
    path('units/<str:id>', UnitDetailView.as_view(), name="unit-detail"),
    path('assign-unit/<str:id>', AssignUnitToTenant.as_view(), name="assign-unit"),
]
