from django.shortcuts import render
from Projects.models import Project

def home_view(request):
    projects = Project.objects.order_by('-date')[:3]
    return render(request, 'index.html', {'projects': projects})

def about_view(request):
    return render(request, 'about.html')

def services_view(request):
    return render(request, 'services.html')