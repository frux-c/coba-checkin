from typing import Any, Iterable
from django.db import models
from django.contrib import admin
from django.db.models import Model
from simple_history.models import HistoricalRecords
from .utils import create_report_in_time_window_for_reports
from django_q.tasks import async_task as q_async_task
import datetime

# Create your models here.
class Device(models.Model):
    name = models.CharField(max_length=50)
    uid = models.CharField(max_length=128, unique=True)
    mac_address = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} ({self.mac_address})"


class Faculty(models.Model):
    name = models.CharField(max_length=50)
    code = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.name} (FC:{self.code})"

class Card(models.Model):
    faculty = models.ForeignKey(
        Faculty, on_delete=models.PROTECT, verbose_name="Faculty"
    )
    card_number = models.IntegerField(verbose_name="Card Number")
    hint = models.CharField(max_length=50, verbose_name="Hint", null=True, blank=True)

    def __str__(self):
        if self.hint is None:
            return f"{self.faculty.name} (FC:{self.faculty.code}) - {self.card_number}"
        return f"{self.faculty.name} (FC:{self.faculty.code}) - {self.hint}"
    
class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=10, verbose_name="ID", null=True, blank=True, help_text="Employee ID")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name="Card", null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="Email")

    @classmethod
    def get_default_employee_pk(cls):
        employee, created = cls.objects.get_or_create(
            first_name="Default", last_name="Employee", employee_id="00000000"
        )
        return employee.pk
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CheckIn(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_DEFAULT, verbose_name="Employee Name", default=Employee.get_default_employee_pk)
    creation_date = models.DateField(auto_now_add=True, verbose_name="Date")
    auto_time_in = models.TimeField(auto_now_add=True, verbose_name="Time In")
    auto_time_out = models.TimeField(
        default=None, null=True, blank=True, verbose_name="Time Out"
    )
    is_on_clock = models.BooleanField(default=True)
    image_proof = models.ImageField(upload_to="images/clockout/", null=True, blank=True)
    timed_out = models.BooleanField(default=False, verbose_name="Auto-Timed Out")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name}"

class ClockSheet(admin.ModelAdmin):
    list_display = (
        "employee",
        "creation_date",
        "auto_time_in",
        "auto_time_out",
        "is_on_clock",
        "timed_out",
    )
    list_filter = ("creation_date",)

class Report(models.Model):
    start_time = models.DateField(default=(datetime.datetime.now()-datetime.timedelta(days=7)).date())
    end_time = models.DateField(default=datetime.datetime.now().date())
    employees = models.ManyToManyField(Employee, verbose_name="Employees", blank=True)
    file = models.FileField(upload_to="reports/", null=True, blank=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)  # Save the report to generate an ID
            q_async_task(create_report_in_time_window_for_reports, self, self.start_time, self.end_time, self.employees.all())
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Generated {self.start_time} - {self.end_time}"

class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('file', )