from django.urls import path
from . import views

"""
Contains URL patterns for forwarding HTTP requests to the respective methods in the views.py file.

Author: Ryan Johnson
"""

urlpatterns = [
    path('', views.index, name="index"),
    path('get_number_classes/', views.get_number_classes, name="get_number_classes"),
    path('get_building_names/', views.get_building_names, name="get_building_names"),
    path('get_used_classrooms/', views.get_used_classrooms, name="get_used_classrooms"),
    path('get_past_time/', views.get_past_time, name="get_past_time"),
    path('get_next_time/', views.get_next_time, name="get_next_time"),
    path('get_classroom_data/', views.get_classroom_data, name="get_classroom_data"),
    path('upload_file/', views.upload_file, name="upload_file"),
]
