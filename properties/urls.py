from django.urls import path

# from property.amenity_views import AmenitiesCreateListView, AmenitiesDetailView

# from .type_views import PropertyTypeCreateListView, PropertyTypeDetailView

from .views import PropertyCreateListView, PropertyDetailView, FileUploadView

urlpatterns = [
    path('upload', FileUploadView.as_view(), name="csv"),
    path('properties/',           PropertyCreateListView.as_view(), name="create-property"),
    path('properties/<str:id>', PropertyDetailView.as_view(),     name="property-detail"),

    # path('my_properties/',  LandlordPropertyListView.as_view(), name="my-properties"),



    # path('property_types/', PropertyTypeCreateListView.as_view(), name="create-type"),
    # path('property_type/<int:id>', PropertyTypeDetailView.as_view(), name="type-detail"),

    # path('amenities/',         AmenitiesCreateListView.as_view(), name="create-amenities"),
    # path('amenities/<int:id>', AmenitiesDetailView.as_view(), name="amenities-detail"),

    # path('property_properties/', get_amenities_properties_owners, name="properties-api")
]
