from django.urls import path
from . import views
from django.urls import path
from .views import upload_csv

urlpatterns = [
    path('get_number_classes/', views.get_number_classes, name="get_number_classes"),
    path('get_time_blocks/', views.get_time_blocks, name="get_time_blocks"),
    path('upload-csv/', upload_csv, name="upload_csv")
]