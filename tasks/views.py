from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Nurse


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
                    return redirect('dashboard')
                messages.error(request, "Invalid credentials")

    return render(request, 'auth.html', {'active_tab': active_tab})


def logout_view(request):
    logout(request)
    return redirect('auth_page')


@login_required(login_url='auth_page')
def dashboard(request):
    tasks = Task.objects.all().order_by('-created_at')
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()
    nurses = Nurse.objects.all()

    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'tasks': tasks[:5],
        'nurses': nurses[:5],
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='auth_page')
def task_list(request):
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'task_list.html', {'tasks': tasks})


@login_required(login_url='auth_page')
def nurse_list(request):
    nurses = Nurse.objects.all()
    return render(request, 'nurse_list.html', {'nurses': nurses})


@login_required(login_url='auth_page')
def reports(request):
    tasks = Task.objects.all().order_by('-created_at')
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

    if request.method == 'POST':
        nurse_id = request.POST.get('nurse')
        patient_name = request.POST.get('patient_name')
        title = request.POST.get('title')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        status = request.POST.get('status')
        priority = request.POST.get('priority')

        nurse = get_object_or_404(Nurse, id=nurse_id)

        Task.objects.create(
            nurse=nurse,
            patient_name=patient_name,
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time if scheduled_time else None,
            status=status,
            priority=priority,
        )

        return redirect('task_list')

    return render(request, 'add_task.html', {'nurses': nurses})


@login_required(login_url='auth_page')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    nurses = Nurse.objects.all()

    if request.method == 'POST':
        nurse_id = request.POST.get('nurse')
        task.nurse = get_object_or_404(Nurse, id=nurse_id)
        task.patient_name = request.POST.get('patient_name')
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