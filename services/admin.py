from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Task)
class Task(admin.ModelAdmin):
    pass

@admin.register(ServiceCase)
class Service(admin.ModelAdmin):
    pass
