from django.shortcuts import render, redirect, get_object_or_404
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


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        return redirect('task_list')

    return render(request, 'delete_task.html', {'task': task})


def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.status = 'completed'
        task.save()

    return redirect('task_list')