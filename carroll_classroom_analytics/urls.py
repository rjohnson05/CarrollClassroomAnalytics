from django.contrib import admin
from django.urls import include, path

from carroll_classroom_analytics import views

"""
URL configuration for carroll_classroom_analytics project.

Contains URL patterns for forwarding HTTP requests to the respective methods in the views.py file. Any URL patterns
containing 'api' are forwarded to the api/views.py file, while the URL patterns used to display the frontend are passed
to views.py in the current directory.

Author: Ryan Johnson
"""

urlpatterns = [
    path('', views.index, name="index"),
    path('used_classrooms/', views.index, name="index"),
    path('classrooms/<str:classroom>', views.index_with_classroom, name="index"),
    path('upload/', views.index, name="index"),

    path('api/', include("api.urls")),
    path('admin/', admin.site.urls),
]
