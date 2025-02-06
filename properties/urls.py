from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from property.amenity_views import AmenitiesCreateListView, AmenitiesDetailView


from .views import (
    PropertyViewSet,
    FileUploadView, PropertyDashboardView
)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='properties')

urlpatterns = [
    path('', include(router.urls)),
    path('upload', FileUploadView.as_view(), name="csv"),
    path('properties-dashboard', PropertyDashboardView.as_view(),     name="property-dashboard"),


    # path('my_properties/',  LandlordPropertyListView.as_view(), name="my-properties"),



    # path('property_types/', PropertyTypeCreateListView.as_view(), name="create-type"),
    # path('property_type/<int:id>', PropertyTypeDetailView.as_view(), name="type-detail"),

    # path('amenities/',         AmenitiesCreateListView.as_view(), name="create-amenities"),
    # path('amenities/<int:id>', AmenitiesDetailView.as_view(), name="amenities-detail"),

    # path('property_properties/', get_amenities_properties_owners, name="properties-api")
]
