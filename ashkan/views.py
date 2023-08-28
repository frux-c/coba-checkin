from django.shortcuts import render
from django.http import HttpResponse
from datetime import date, time, datetime
from .models import *

# https://www.pluralsight.com/guides/introduction-to-django-views

# database management:
# https://docs.djangoproject.com/en/4.2/topics/forms/
# https://docs.djangoproject.com/en/4.2/topics/db/queries/ --> queries in Python (not SQL)

def checkinForm(request):
    print(datetime.time)
    print(datetime.date)

    return render(request, './ashkan/home.html', {
        "names": Student.objects.all(),
        "invalid": False
    })

# handle checkin data

def handle_checkin(request):
    data = request.POST
    name = data['name']
    first_name, last_name = name.split(' ', 1);
    id = data['ID']
    currentTime = datetime.now().strftime("%H:%M")

    print("first_name:", first_name)
    print("last_name: ", last_name)

    # check if user + id combo is valid
    database_match = Student.objects.get(**{
        "first_name": first_name,
        "last_name": last_name
    })

    if (database_match._id == id):
        # correct name + id
        return render(request, './ashkan/welcome.html', {
            'name': data['name']
        })
    else:
        # incorrect name + id
        return HttpResponse("whoops, it's wrong!")
