from django.contrib import messages
import base64
import binascii
import json
from functools import wraps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Nurse, UserProfile, Patient


def get_or_create_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def parse_request_data(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return request.POST.dict()


def api_auth_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Basic '):
            encoded_creds = auth_header.split(' ', 1)[1].strip()
            try:
                decoded = base64.b64decode(encoded_creds).decode('utf-8')
                username_or_email, password = decoded.split(':', 1)
            except (ValueError, UnicodeDecodeError, binascii.Error):
                return JsonResponse({'error': 'Invalid Basic Auth header.'}, status=401)

            user_qs = User.objects.filter(
                Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)
            )
            if user_qs.exists():
                user = authenticate(request, username=user_qs.first().username, password=password)
                if user is not None:
                    request.user = user
                    return view_func(request, *args, **kwargs)

        return JsonResponse({'error': 'Authentication required.'}, status=401)

    return _wrapped


def nurse_to_dict(nurse):
    return {
        'id': nurse.id,
        'full_name': nurse.full_name,
        'email': nurse.email,
        'department': nurse.department,
    }


def patient_to_dict(patient):
    return {
        'id': patient.id,
        'full_name': patient.full_name,
        'age': patient.age,
        'gender': patient.gender,
        'contact_information': patient.contact_information,
        'address': patient.address,
        'medical_notes': patient.medical_notes,
        'created_at': patient.created_at.isoformat(),
    }


def task_to_dict(task):
    return {
        'id': task.id,
        'nurse_id': task.nurse_id,
        'nurse_name': task.nurse.full_name if task.nurse_id else None,
        'patient_id': task.patient_id,
        'patient_name': task.patient_name,
        'title': task.title,
        'description': task.description,
        'scheduled_date': task.scheduled_date.isoformat(),
        'scheduled_time': task.scheduled_time.isoformat() if task.scheduled_time else None,
        'status': task.status,
        'priority': task.priority,
        'created_at': task.created_at.isoformat(),
    }


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


@csrf_exempt
@api_auth_required
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


@csrf_exempt
@api_auth_required
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


@csrf_exempt
@api_auth_required
@require_http_methods(["GET", "POST"])
def nurses_api(request):
    if request.method == 'GET':
        nurses = Nurse.objects.all().order_by('full_name')
        return JsonResponse({'results': [nurse_to_dict(nurse) for nurse in nurses]})

    payload = parse_request_data(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    full_name = (payload.get('full_name') or '').strip()
    email = (payload.get('email') or '').strip().lower()
    department = (payload.get('department') or '').strip()

    errors = {}
    if not full_name:
        errors['full_name'] = 'full_name is required.'
    if not email:
        errors['email'] = 'email is required.'
    elif Nurse.objects.filter(email__iexact=email).exists():
        errors['email'] = 'A nurse with this email already exists.'

    if errors:
        return JsonResponse({'errors': errors}, status=400)

    nurse = Nurse.objects.create(
        full_name=full_name,
        email=email,
        department=department or None,
    )
    return JsonResponse({'data': nurse_to_dict(nurse)}, status=201)


@csrf_exempt
@api_auth_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def nurse_detail_api(request, nurse_id):
    nurse = get_object_or_404(Nurse, id=nurse_id)

    if request.method == 'GET':
        return JsonResponse({'data': nurse_to_dict(nurse)})

    if request.method == 'DELETE':
        nurse.delete()
        return JsonResponse({'message': 'Nurse deleted successfully.'})

    payload = parse_request_data(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    if 'full_name' in payload:
        nurse.full_name = (payload.get('full_name') or '').strip()
    if 'email' in payload:
        new_email = (payload.get('email') or '').strip().lower()
        if not new_email:
            return JsonResponse({'errors': {'email': 'email is required.'}}, status=400)
        if Nurse.objects.exclude(id=nurse.id).filter(email__iexact=new_email).exists():
            return JsonResponse({'errors': {'email': 'A nurse with this email already exists.'}}, status=400)
        nurse.email = new_email
    if 'department' in payload:
        nurse.department = (payload.get('department') or '').strip() or None

    if not nurse.full_name:
        return JsonResponse({'errors': {'full_name': 'full_name is required.'}}, status=400)

    nurse.save()
    return JsonResponse({'data': nurse_to_dict(nurse)})


@csrf_exempt
@api_auth_required
@require_http_methods(["GET", "POST"])
def patients_api(request):
    if request.method == 'GET':
        patients = Patient.objects.all().order_by('-created_at')
        return JsonResponse({'results': [patient_to_dict(patient) for patient in patients]})

    payload = parse_request_data(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    required_fields = ['full_name', 'age', 'gender', 'contact_information', 'address']
    errors = {}
    for field in required_fields:
        if not str(payload.get(field, '')).strip():
            errors[field] = f'{field} is required.'

    try:
        age = int(payload.get('age', 0))
        if age < 0:
            raise ValueError
    except (TypeError, ValueError):
        errors['age'] = 'age must be a valid non-negative integer.'
        age = 0

    if errors:
        return JsonResponse({'errors': errors}, status=400)

    patient = Patient.objects.create(
        full_name=payload.get('full_name').strip(),
        age=age,
        gender=payload.get('gender').strip(),
        contact_information=payload.get('contact_information').strip(),
        address=payload.get('address').strip(),
        medical_notes=(payload.get('medical_notes') or '').strip() or None,
    )
    return JsonResponse({'data': patient_to_dict(patient)}, status=201)


@csrf_exempt
@api_auth_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def patient_detail_api(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'GET':
        return JsonResponse({'data': patient_to_dict(patient)})

    if request.method == 'DELETE':
        if patient.tasks.exists():
            return JsonResponse(
                {'error': 'This patient cannot be deleted because there are tasks linked to their profile.'},
                status=400,
            )
        patient.delete()
        return JsonResponse({'message': 'Patient deleted successfully.'})

    payload = parse_request_data(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    if 'full_name' in payload:
        patient.full_name = (payload.get('full_name') or '').strip()
    if 'age' in payload:
        try:
            patient.age = int(payload.get('age'))
            if patient.age < 0:
                raise ValueError
        except (TypeError, ValueError):
            return JsonResponse({'errors': {'age': 'age must be a valid non-negative integer.'}}, status=400)
    if 'gender' in payload:
        patient.gender = (payload.get('gender') or '').strip()
    if 'contact_information' in payload:
        patient.contact_information = (payload.get('contact_information') or '').strip()
    if 'address' in payload:
        patient.address = (payload.get('address') or '').strip()
    if 'medical_notes' in payload:
        patient.medical_notes = (payload.get('medical_notes') or '').strip() or None

    required_errors = {}
    if not patient.full_name:
        required_errors['full_name'] = 'full_name is required.'
    if patient.age is None:
        required_errors['age'] = 'age is required.'
    if not patient.gender:
        required_errors['gender'] = 'gender is required.'
    if not patient.contact_information:
        required_errors['contact_information'] = 'contact_information is required.'
    if not patient.address:
        required_errors['address'] = 'address is required.'
    if required_errors:
        return JsonResponse({'errors': required_errors}, status=400)

    patient.save()
    patient.tasks.update(patient_name=patient.full_name)
    return JsonResponse({'data': patient_to_dict(patient)})


@csrf_exempt
@api_auth_required
@require_http_methods(["GET", "POST"])
def tasks_api(request):
    if request.method == 'GET':
        tasks = Task.objects.select_related('nurse', 'patient').all().order_by('-created_at')
        return JsonResponse({'results': [task_to_dict(task) for task in tasks]})

    payload = parse_request_data(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    required_fields = ['nurse_id', 'patient_id', 'title', 'description', 'scheduled_date']
    errors = {}
    for field in required_fields:
        if not str(payload.get(field, '')).strip():
            errors[field] = f'{field} is required.'
    if errors:
        return JsonResponse({'errors': errors}, status=400)

    nurse = get_object_or_404(Nurse, id=payload.get('nurse_id'))
    patient = get_object_or_404(Patient, id=payload.get('patient_id'))

    task = Task.objects.create(
        nurse=nurse,
        patient=patient,
        patient_name=patient.full_name,
        title=(payload.get('title') or '').strip(),
        description=(payload.get('description') or '').strip(),
        scheduled_date=payload.get('scheduled_date'),
        scheduled_time=(payload.get('scheduled_time') or '').strip() or None,
        status=(payload.get('status') or '').strip() or 'pending',
        priority=(payload.get('priority') or '').strip() or 'Medium',
    )
    task.refresh_from_db()
    return JsonResponse({'data': task_to_dict(task)}, status=201)


@csrf_exempt
@api_auth_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def task_detail_api(request, task_id):
    task = get_object_or_404(Task.objects.select_related('nurse', 'patient'), id=task_id)

    if request.method == 'GET':
        return JsonResponse({'data': task_to_dict(task)})

    if request.method == 'DELETE':
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully.'})

    payload = parse_request_data(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    if 'nurse_id' in payload:
        task.nurse = get_object_or_404(Nurse, id=payload.get('nurse_id'))
    if 'patient_id' in payload:
        task.patient = get_object_or_404(Patient, id=payload.get('patient_id'))
        task.patient_name = task.patient.full_name
    if 'title' in payload:
        task.title = (payload.get('title') or '').strip()
    if 'description' in payload:
        task.description = (payload.get('description') or '').strip()
    if 'scheduled_date' in payload:
        task.scheduled_date = payload.get('scheduled_date')
    if 'scheduled_time' in payload:
        task.scheduled_time = (payload.get('scheduled_time') or '').strip() or None
    if 'status' in payload:
        task.status = (payload.get('status') or '').strip()
    if 'priority' in payload:
        task.priority = (payload.get('priority') or '').strip()

    required_errors = {}
    if not task.title:
        required_errors['title'] = 'title is required.'
    if not task.description:
        required_errors['description'] = 'description is required.'
    if not task.scheduled_date:
        required_errors['scheduled_date'] = 'scheduled_date is required.'
    if required_errors:
        return JsonResponse({'errors': required_errors}, status=400)

    task.save()
    task.refresh_from_db()
    return JsonResponse({'data': task_to_dict(task)})