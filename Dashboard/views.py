from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import OperationalError, ProgrammingError
from Contacts.models import Clients
from Projects.models import Project
from Projects.forms import ProjectForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)


# ADMIN AUTHORIZATION & AUTHENTICATION
def login_admin(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "All fields are required!")
            return render(request, "dashboard/login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard:overview')

        messages.error(request, "Invalid username or password, please check your credentials and try again!")
        return render(request, "dashboard/login.html")
    
    return render(request, 'dashboard/login.html')


# LOGOUT
@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('dashboard:login')


# OVERVIEW DASHBOARD
@login_required
def overview_view(request):
    try:
        total_contacts = Clients.objects.count()
        total_projects = Project.objects.count()
        recent_projects = Project.objects.order_by('-date')[:5]
        recent_contacts = Clients.objects.order_by('-id')[:5]
    except (OperationalError, ProgrammingError) as exc:
        logger.error("Dashboard overview DB error: %s", exc)
        messages.error(request, "Could not load dashboard data. Please check that migrations have been run on the database.")
        total_contacts = 0
        total_projects = 0
        recent_projects = []
        recent_contacts = []

    context = {
        "contacts": total_contacts,
        "projects": total_projects,
        "recent_projects": recent_projects,
        "recent_contacts": recent_contacts,
    }
    return render(request, 'admin/overview.html', context)


# PROJECTS MANAGEMENT
@login_required
def projects_view(request):
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '')
    )

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                project = form.save()
            except Exception as exc:
                logger.error("Error saving project (possible Cloudinary issue): %s", exc)
                err_msg = (
                    "Failed to upload the cover photo. Please check Cloudinary credentials "
                    "are set correctly in environment variables, then try again."
                )
                messages.error(request, err_msg)
                if is_ajax:
                    return JsonResponse({'success': False, 'message': err_msg, 'errors': {}}, status=500)
                projects = Project.objects.all().order_by('-date')
                return render(request, 'admin/projects.html', {'form': form, 'projects': projects})

            messages.success(request, f'Project "{project.title}" was added successfully.')
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Project "{project.title}" was added successfully.',
                    'redirect_url': '/dashboard/projects/',
                })
            return redirect('dashboard:projects')

        messages.error(request, 'Project was not added. Please correct the highlighted fields.')
        if is_ajax:
            errors = {field: [str(err) for err in errs] for field, errs in form.errors.items()}
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors in the form.',
                'errors': errors,
            }, status=400)
    else:
        form = ProjectForm()

    projects = Project.objects.all().order_by('-date')
    return render(request, 'admin/projects.html', {
        'form': form,
        'projects': projects,
    })


# DELETE PROJECT
@login_required
def delete_project_view(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        title = project.title
        project.delete()
        messages.success(request, f'Project "{title}" was deleted.')
    return redirect('dashboard:projects')


# CONTACTS INBOX
@login_required
def contacts_view(request):
    try:
        contacts = Clients.objects.all().order_by('-id')
        total = contacts.count()
    except (OperationalError, ProgrammingError) as exc:
        logger.error("Contacts inbox DB error: %s", exc)
        messages.error(request, "Could not load messages. Please check that database migrations have been applied.")
        contacts = []
        total = 0
    return render(request, 'admin/contacts.html', {
        'contacts': contacts,
        'total_contacts': total,
    })


# DELETE CONTACT MESSAGE
@login_required
def delete_contact_view(request, pk):
    if request.method == 'POST':
        contact = get_object_or_404(Clients, pk=pk)
        contact.delete()
        messages.success(request, 'Contact message deleted.')
    return redirect('dashboard:contacts')
