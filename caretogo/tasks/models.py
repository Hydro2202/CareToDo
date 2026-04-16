from django.db import models


class Nurse(models.Model):
    full_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.full_name


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='tasks')
    patient_name = models.CharField(max_length=100)
    task_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    schedule = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.task_description[:30]}"