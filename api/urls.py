from django.urls import path
from . import views

"""
Provides URL patterns for sending HTTP requests to the respective methods in the views.py file.
"""
urlpatterns = [
    path('get_number_classes/', views.get_number_classes, name="get_number_classes"),
    path('get_building_names/', views.get_building_names, name="get_building_names"),
    path('get_used_classrooms/', views.get_used_classrooms, name="get_used_classrooms"),
    path('get_classroom_data/', views.get_classroom_data, name="get_classroom_data"),
]