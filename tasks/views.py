from django.shortcuts import render, redirect
from .models import Task, Nurse


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


def task_list(request):
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'task_list.html', {'tasks': tasks})


def nurse_list(request):
    nurses = Nurse.objects.all()
    return render(request, 'nurse_list.html', {'nurses': nurses})


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

        nurse = Nurse.objects.get(id=nurse_id)

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