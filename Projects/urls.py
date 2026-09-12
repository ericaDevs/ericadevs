from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.projects_views, name="projects"),
    path('<slug:slug>/', views.project_detail, name="detail"),
]