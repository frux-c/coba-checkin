from rest_framework import serializers
from .models import Employee, CheckIn

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('first_name', 'last_name')

class CheckInSerializer(serializers.ModelSerializer):
    employee = serializers.StringRelatedField()
    class Meta:
        model = CheckIn
        fields = ('employee', 'creation_date', 'is_on_clock', 'auto_time_in', 'auto_time_out', 'timed_out')
