from django.contrib import admin
from .models import Nurse, Task, Patient

admin.site.register(Nurse)
admin.site.register(Task)
admin.site.register(Patient)