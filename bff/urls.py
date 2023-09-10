from django.urls import path

from .views import getAssignments

urlpatterns = [
    path('assignments/<str:id>', getAssignments, name="unit-assignments"),
]
