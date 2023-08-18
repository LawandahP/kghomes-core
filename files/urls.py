from django.urls import path
from .views import (FilesCreateListView)

urlpatterns = [
    path('images/',  FilesCreateListView.as_view(), name="images"),

]