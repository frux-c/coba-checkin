from django.shortcuts import render
from django.db import models
from django.contrib import admin
from datetime import datetime
from simple_history.models import HistoricalRecords
import json


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

    def __str__(self):
        return f"{self.faculty.name} (FC:{self.faculty.code}) - {self.card_number}"
    
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    _id = models.CharField(max_length=8, verbose_name="ID", blank=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name="Card", null=True, blank=True)
    email = models.EmailField(
        unique=True, null=True, blank=True, verbose_name="UTEP Email"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CheckIn(models.Model):
    user = models.ForeignKey(
        Student, on_delete=models.PROTECT, verbose_name="Student/Employee Name"
    )
    date_created = models.DateField(auto_now_add=True, verbose_name="Date")
    auto_time_in = models.TimeField(auto_now_add=True, verbose_name="Time In")
    auto_time_out = models.TimeField(
        default=None, null=True, blank=True, verbose_name="Time Out"
    )
    is_on_clock = models.BooleanField(default=True)
    image_proof = models.ImageField(upload_to="images/clockout/", null=True, blank=True)
    timed_out = models.BooleanField(default=False, verbose_name="Auto-Timed Out")
    history = HistoricalRecords()

    def serialize(self):
        rtn = {}
        rtn["name"] = str(self.user)
        rtn["date_created"] = str(self.date_created)
        rtn["time_in"] = str(self.auto_time_in)
        rtn["time_out"] = "-"
        if self.auto_time_out:
            rtn["time_out"] = str(self.auto_time_out)
        return rtn

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# def generate_report(modeladmin, request, queryset):
#     qs = list(queryset)
#     serialized_queryset = [q.serialize() for q in qs]
#     return render(request, "report.html", {"query": json.dumps(serialized_queryset)})


# generate_report.short_description = "Generate Selected Report"


class ClockSheet(admin.ModelAdmin):
    list_display = (
        "user",
        "date_created",
        "auto_time_in",
        "auto_time_out",
        "is_on_clock",
        "timed_out",
    )
    list_filter = ("date_created",)
    # actions = [generate_report]