from django.db import models
from django.contrib import admin
from simple_history.models import HistoricalRecords
from hashlib import sha256

class SHA256HashedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 128
        super(SHA256HashedCharField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return value
        return sha256(str(value).encode("utf-8")).hexdigest()

# Create your models here.
class Device(models.Model):
    name = models.CharField(max_length=50)
    uid = models.CharField(max_length=128, unique=True)
    mac_address = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} ({self.mac_address})"


class Faculty(models.Model):
    name = models.CharField(max_length=50)
    code = SHA256HashedCharField(unique=True)

    def __str__(self):
        return f"{self.name} (FC:{self.code})"

class Card(models.Model):
    faculty = models.ForeignKey(
        Faculty, on_delete=models.PROTECT, verbose_name="Faculty"
    )
    card_number = SHA256HashedCharField(verbose_name="Card Number")
    hint = models.CharField(max_length=50, verbose_name="Hint", null=True, blank=True)
    def __str__(self):
        if self.hint is None:
            return f"{self.faculty.name} (FC:{self.faculty.code}) - {self.card_number}"
        return f"{self.faculty.name} (FC:{self.faculty.code}) - {self.hint}"
    
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    _id = SHA256HashedCharField(verbose_name="ID", blank=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name="Card", null=True, blank=True)
    email = models.EmailField(
        unique=True, null=True, blank=True, verbose_name="Email"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CheckIn(models.Model):
    user = models.ForeignKey(
        Student, on_delete=models.PROTECT, verbose_name="Student/Employee Name"
    )
    creation_date = models.DateField(auto_now_add=True, verbose_name="Date")
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
        rtn["creation_date"] = str(self.creation_date)
        rtn["time_in"] = str(self.auto_time_in)
        rtn["time_out"] = "-"
        if self.auto_time_out:
            rtn["time_out"] = str(self.auto_time_out)
        return rtn

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class ClockSheet(admin.ModelAdmin):
    list_display = (
        "user",
        "creation_date",
        "auto_time_in",
        "auto_time_out",
        "is_on_clock",
        "timed_out",
    )
    list_filter = ("creation_date",)