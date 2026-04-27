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
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:patient_id>/edit/', views.edit_patient, name='edit_patient'),
    path('patients/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    path('api/profile/', views.profile_data, name='profile_data'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
    path('api/nurses/', views.nurses_api, name='nurses_api'),
    path('api/nurses/<int:nurse_id>/', views.nurse_detail_api, name='nurse_detail_api'),
    path('api/patients/', views.patients_api, name='patients_api'),
    path('api/patients/<int:patient_id>/', views.patient_detail_api, name='patient_detail_api'),
    path('api/tasks/', views.tasks_api, name='tasks_api'),
    path('api/tasks/<int:task_id>/', views.task_detail_api, name='task_detail_api'),
]