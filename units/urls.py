from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UnitViewSet, AssignUnitToTenant

router = DefaultRouter()
router.register(r'units', UnitViewSet, basename='units')

urlpatterns = [
    path('', include(router.urls)),
    path('assign-unit/<str:id>', AssignUnitToTenant.as_view(), name="assign-unit"),
]
