"""
URL configuration for Portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import serve
from django.urls import path, include, re_path
from . import views
from Dashboard import views as dashboard_views

app_name = "main"

urlpatterns = [
    path('admin/', dashboard_views.login_admin, name = "admin"),
    path('', views.home_view, name="home"),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('dashboard/', include('Dashboard.urls')),
    path('projects/', include('Projects.urls')),
    path('contacts/', include('Contacts.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
