from django.contrib import admin
from .models import Employee, CheckIn, ClockSheet, Device, Faculty, Card

admin.site.site_header = "COBA Check-in Administration"
admin.site.site_title = "COBA Check-in Admin"
admin.site.index_title = "COBA App Tables"

# Register your models here.
admin.site.register(Employee)
admin.site.register(CheckIn, ClockSheet)
admin.site.register(Device)
admin.site.register(Faculty)
admin.site.register(Card)
