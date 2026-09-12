from django.shortcuts import get_object_or_404, render
# pyrefly: ignore [missing-import]
from . models import Project

# Create your views here.
def projects_views(request):
    projects = Project.objects.all().order_by('-date')
    return render(request, 'pages/projects.html', {'projects': projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    related_projects = Project.objects.exclude(id=project.id).order_by('-date')[:3]
    return render(request, 'pages/projectsdetails.html', {
        'project': project,
        'related_projects': related_projects,
    })