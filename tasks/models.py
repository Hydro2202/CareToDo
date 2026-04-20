from django.db import models
from django.contrib.auth.models import User

class Nurse(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.full_name


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='tasks')
    patient_name = models.CharField(max_length=150)
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.user.email} profile"