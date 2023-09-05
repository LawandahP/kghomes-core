from django.urls import path
from .views import FilesCreateListView, FileDetailsView

urlpatterns = [
    path('images/',  FilesCreateListView.as_view(), name="images"),
    path('images/<str:id>', FilesCreateListView.as_view(), name="property_images"),
    path('delete-image/<str:id>',  FileDetailsView.as_view(), name="delete_images"),

]