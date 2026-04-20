from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth_page, name='auth_page'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('nurses/', views.nurse_list, name='nurse_list'),
    path('reports/', views.reports, name='reports'),
    path('api/profile/', views.profile_data, name='profile_data'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
]