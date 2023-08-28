from django.contrib import admin
from .models import Student,CheckIn,ClockSheet


# Register your models here.
admin.site.register(Student)
admin.site.register(CheckIn,ClockSheet)