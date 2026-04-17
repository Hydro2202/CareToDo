from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('nurses/', views.nurse_list, name='nurse_list'),
    path('reports/', views.reports, name='reports'),
]