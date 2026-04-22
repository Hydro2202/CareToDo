from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Nurse, UserProfile, Patient


def get_or_create_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def get_authenticated_email(request, user):
    # Keep email sourced from authenticated context without duplicating DB fields.
    return user.email or request.session.get('login_email') or user.username


def auth_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    active_tab = request.POST.get('auth_action', 'login')

    if request.method == 'POST':
        if active_tab == 'signup':
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not full_name or not email or not password or not confirm_password:
                messages.error(request, "Please fill out all signup fields.")
            elif password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).exists():
                messages.error(request, "Account already exists. Please log in.")
                active_tab = 'login'
            else:
                # Uses Django's secure password hashing automatically.
                User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name,
                )
                messages.success(request, "Account created. Please log in.")
                active_tab = 'login'
        else:
            email_or_username = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')

            user_qs = User.objects.filter(
                Q(username__iexact=email_or_username) | Q(email__iexact=email_or_username)
            )

            if not user_qs.exists():
                messages.error(request, "Account not found. Please create an account first.")
            else:
                user_obj = user_qs.first()
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    request.session['login_email'] = user_obj.email or email_or_username
                    return redirect('dashboard')
                messages.error(request, "Invalid credentials")

    return render(request, 'auth.html', {'active_tab': active_tab})


def logout_view(request):
    request.session.pop('login_email', None)
    logout(request)
    return redirect('auth_page')


@login_required(login_url='auth_page')
def dashboard(request):
    tasks = Task.objects.select_related('patient').all().order_by('-created_at')
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()
    nurses = Nurse.objects.all()

    profile = get_or_create_user_profile(request.user)
    display_name = request.user.first_name or request.user.username

    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'tasks': tasks[:5],
        'nurses': nurses[:5],
        'profile_name': display_name,
        'profile_department': profile.department or "Not set",
        'profile_role': "RN",
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='auth_page')
def task_list(request):
    tasks = Task.objects.select_related('patient').all().order_by('-created_at')
    return render(request, 'task_list.html', {'tasks': tasks})


@login_required(login_url='auth_page')
def nurse_list(request):
    nurses = Nurse.objects.all()
    return render(request, 'nurse_list.html', {'nurses': nurses})


@login_required(login_url='auth_page')
def reports(request):
    tasks = Task.objects.select_related('patient').all().order_by('-created_at')
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'reports.html', context)


@login_required(login_url='auth_page')
def add_task(request):
    nurses = Nurse.objects.all()
    patients = Patient.objects.all().order_by('full_name')

    if request.method == 'POST':
        nurse_id = request.POST.get('nurse')
        patient_id = request.POST.get('patient')
        title = request.POST.get('title')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        status = request.POST.get('status')
        priority = request.POST.get('priority')

        nurse = get_object_or_404(Nurse, id=nurse_id)
        patient = get_object_or_404(Patient, id=patient_id)

        Task.objects.create(
            nurse=nurse,
            patient=patient,
            patient_name=patient.full_name,
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time if scheduled_time else None,
            status=status,
            priority=priority,
        )

        return redirect('task_list')

    return render(request, 'add_task.html', {'nurses': nurses, 'patients': patients})


@login_required(login_url='auth_page')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    nurses = Nurse.objects.all()
    patients = Patient.objects.all().order_by('full_name')

    if request.method == 'POST':
        nurse_id = request.POST.get('nurse')
        patient_id = request.POST.get('patient')
        task.nurse = get_object_or_404(Nurse, id=nurse_id)
        task.patient = get_object_or_404(Patient, id=patient_id)
        task.patient_name = task.patient.full_name
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.scheduled_date = request.POST.get('scheduled_date')
        task.scheduled_time = request.POST.get('scheduled_time') or None
        task.status = request.POST.get('status')
        task.priority = request.POST.get('priority')
        task.save()

        return redirect('task_list')

    context = {
        'task': task,
        'nurses': nurses,
        'patients': patients,
    }
    return render(request, 'edit_task.html', context)


@login_required(login_url='auth_page')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        return redirect('task_list')

    return render(request, 'delete_task.html', {'task': task})


@login_required(login_url='auth_page')
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.status = 'completed'
        task.save()

    return redirect('task_list')


@login_required(login_url='auth_page')
def patient_list(request):
    patients = Patient.objects.all().order_by('-created_at')
    selected_patient = None
    selected_patient_tasks = []
    patient_id = request.GET.get('view')

    if patient_id:
        selected_patient = get_object_or_404(Patient, id=patient_id)
        selected_patient_tasks = selected_patient.tasks.select_related('nurse').order_by('-created_at')

    context = {
        'patients': patients,
        'selected_patient': selected_patient,
        'selected_patient_tasks': selected_patient_tasks,
    }
    return render(request, 'patient_list.html', context)


@login_required(login_url='auth_page')
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient_tasks = patient.tasks.select_related('nurse').order_by('-created_at')
    return render(
        request,
        'patient_detail.html',
        {
            'patient': patient,
            'patient_tasks': patient_tasks,
        },
    )


@login_required(login_url='auth_page')
def add_patient(request):
    if request.method == 'POST':
        Patient.objects.create(
            full_name=request.POST.get('full_name'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender'),
            contact_information=request.POST.get('contact_information'),
            address=request.POST.get('address'),
            medical_notes=request.POST.get('medical_notes') or None,
        )
        return redirect('patient_list')

    return render(request, 'add_patient.html')


@login_required(login_url='auth_page')
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        patient.full_name = request.POST.get('full_name')
        patient.age = request.POST.get('age')
        patient.gender = request.POST.get('gender')
        patient.contact_information = request.POST.get('contact_information')
        patient.address = request.POST.get('address')
        patient.medical_notes = request.POST.get('medical_notes') or None
        patient.save()

        # Keep denormalized task display name synchronized.
        patient.tasks.update(patient_name=patient.full_name)
        return redirect('patient_list')

    return render(request, 'edit_patient.html', {'patient': patient})


@login_required(login_url='auth_page')
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    linked_tasks_count = patient.tasks.count()

    if request.method == 'POST':
        if linked_tasks_count > 0:
            messages.error(
                request,
                "This patient cannot be deleted because there are tasks linked to their profile."
            )
            return redirect('patient_list')

        patient.delete()
        messages.success(request, "Patient deleted successfully.")
        return redirect('patient_list')

    return render(
        request,
        'delete_patient.html',
        {'patient': patient, 'linked_tasks_count': linked_tasks_count},
    )


@login_required(login_url='auth_page')
@require_http_methods(["GET"])
def profile_data(request):
    profile = get_or_create_user_profile(request.user)
    display_name = request.user.first_name or request.user.username

    return JsonResponse({
        'id': request.user.id,
        'name': display_name,
        'email': get_authenticated_email(request, request.user),
        'department': profile.department,
        'role': "RN",
    })


@login_required(login_url='auth_page')
@require_http_methods(["POST"])
def update_profile(request):
    name = request.POST.get('name', '').strip()
    department = request.POST.get('department', '').strip()

    errors = {}
    if not name:
        errors['name'] = "Name is required."
    elif len(name) > 150:
        errors['name'] = "Name must be 150 characters or less."

    if not department:
        errors['department'] = "Department is required."
    elif len(department) > 100:
        errors['department'] = "Department must be 100 characters or less."

    if errors:
        return JsonResponse({'errors': errors}, status=400)

    profile = get_or_create_user_profile(request.user)
    request.user.first_name = name
    request.user.save(update_fields=['first_name'])
    profile.department = department
    profile.save(update_fields=['department'])

    return JsonResponse({
        'message': "Profile updated successfully.",
        'profile': {
            'id': request.user.id,
            'name': request.user.first_name,
            'email': get_authenticated_email(request, request.user),
            'department': profile.department,
            'role': "RN",
        }
    })