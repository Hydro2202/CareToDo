from rest_framework import serializers
from .models import Nurse, Task


class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    nurse_name = serializers.CharField(source='nurse.full_name', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'