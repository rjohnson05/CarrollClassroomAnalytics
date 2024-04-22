"""
URL configuration for carroll_classroom_analytics project.

The `urlpatterns` list routes URLs to views.

Author: Ryan Johnson
"""
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', include("api.urls")),
    path('api/', include("api.urls")),
    path('admin/', admin.site.urls),
]
