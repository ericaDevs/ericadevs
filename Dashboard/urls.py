from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.login_admin, name="login"),
    path('overview/', views.overview_view, name='overview'),
    path('projects/', views.projects_view, name='projects'),
    path('projects/<int:pk>/delete/', views.delete_project_view, name='delete_project'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('contacts/<int:pk>/delete/', views.delete_contact_view, name='delete_contact'),
    path('logout/', views.logout_user, name='logout'),
]
