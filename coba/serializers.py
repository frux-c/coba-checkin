from rest_framework import serializers
from .models import *

class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ['employee', 'is_on_clock', 'auto_time_in', 'auto_time_out', 'timed_out']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name']
