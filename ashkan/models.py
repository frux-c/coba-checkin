from django.db import models

# Create your models here.
from django.shortcuts import render
from django.db import models
from django.contrib import admin
from datetime import datetime
from simple_history.models import HistoricalRecords
import json

# initial setup
# https://techvidvan.com/tutorials/django-database-connectivity/

# adding / querying data
# 

# Create your models here.
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    _id = models.CharField(max_length=8,verbose_name="ID")
    email = models.EmailField(unique=True,null=True,blank=True,verbose_name="UTEP Email")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class CheckIn(models.Model):
    user = models.ForeignKey(Student,on_delete=models.CASCADE,verbose_name="Student/Employee Name")
    date_created = models.DateField(auto_now_add=True, verbose_name="Date")
    time_in = models.TimeField(verbose_name="Time In",default=datetime.now())
    time_out = models.TimeField(default=None,null=True,blank=True, verbose_name="Time Out")
    is_on_clock = models.BooleanField(default=True)
    image_proof = models.ImageField(upload_to="images/clockout/",null=True,blank=True)
    timed_out = models.BooleanField(default=False,verbose_name="Auto-Timed Out")
    history = HistoricalRecords()

    def serialize(self):
        rtn = {}
        rtn['Name'] = str(self.user)
        rtn['Date Created'] = str(self.date_created)
        rtn['Real Time In'] = str(self.time_in)
        if self.time_out:
            rtn['Real Time Out'] = str(self.time_out)
        return rtn
        rtn["Auto Signed Out"] = str(self.timed_out)
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

def generate_report(modeladmin,request,queryset):
    qs = list(queryset)
    serialized_queryset = [q.serialize() for q in qs]
    return render(request,"report.html",{"query" : json.dumps(serialized_queryset)})

generate_report.short_description = "Generate Selected Report"
class ClockSheet(admin.ModelAdmin):
    list_display = ("user","date_created","time_in","time_out","is_on_clock","timed_out")
    list_filter = ('date_created',)
    actions = [generate_report]

admin.site.site_header = "COBA Check-in Administration"
