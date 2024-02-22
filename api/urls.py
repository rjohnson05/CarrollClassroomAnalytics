from django.urls import path
from . import views

urlpatterns = [
    path('get_number_classes/', views.get_number_classes, name="get_number_classes"),
    path('get_time_blocks/', views.get_time_blocks, name="get_time_blocks"),
    path('upload_csv/', views.upload_csv, name="upload_csv"),
]