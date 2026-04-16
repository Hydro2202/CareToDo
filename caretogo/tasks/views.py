from django.shortcuts import render
from rest_framework import viewsets
from .models import Nurse, Task
from .serializers import NurseSerializer, TaskSerializer


def home(request):
    return render(request, 'index.html')


class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer