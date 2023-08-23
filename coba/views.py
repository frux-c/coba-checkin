from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from .models import Student,CheckIn
from datetime import datetime,timedelta
from datetime import date
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from channels.layers import get_channel_layer # channel websocket import
from asgiref.sync import async_to_sync, sync_to_async
import json
import asyncio
from deprecated import deprecated


# Create your views here.
class CheckInView(TemplateView):
    """

    CheckInView : Renders the home page from templates using the 
    TemplateView Object as parent : read django TemplateView for more Info,
    and also passes the student query for the student drop down

    """
    template_name="home.html"
    
    def get_context_data(self, **kwargs):
        kwargs["students"] = Student.objects.all()
        return super().get_context_data(**kwargs)
        

@require_POST
def checkInWebhook(request):
    """"

    checkInWebhook : Returns true or false depending if student/employee is on clock or not. 
    accepts json payload with key "student" and value is a full name.
        Ex. "John Smith" : {"student" : "John Smith"},
        NOTE : Student has to already exist in database.

    """
    payload = json.loads(request.body)
    if payload["student"] == "":
        return HttpResponse(status=200)
    #get Student Name and check if they're on clock
    student = payload["student"].split(" ",1)
    student_object = get_object_or_404(Student,
                                first_name = student[0],
                                last_name = student[-1])
    check = CheckIn.objects.filter(user=student_object,
                                    is_on_clock = True)
    if check.exists():
        return JsonResponse({"on_clock" : True})
    return JsonResponse({"on_clock" : False})


@require_POST
def checkOutWebhook(request):
    """
    checkOutWebhook : downloads and maps a checkout image to a checkin object

    """
    img = request.FILES['snap']
    fss = FileSystemStorage()
    payload = request.POST.dict()
    if payload["checkin_pk"] == "":
        return HttpResponse(status=401)
    check = CheckIn.objects.filter(pk=int(payload["checkin_pk"]))
    if check.exists():
        check = check[0]
        file = fss.save(f"{check.user.last_name}-{check.user.first_name}-{date.today()}.jpg", img)
        check.image_proof = file
        check.auto_time_out = datetime.now()
        check.save()
    return HttpResponse(status=200)

def acceptCheckForm(request):
    """
        acceptCheckForm : signs in/out students depending on the state
    """
    channel_layer = get_channel_layer()
    payload = request.POST.dict()
    if payload.get("student") is None:
        return render(request,"checkLanding.html")
    student = payload["student"].split(" ",1)
    id_num = payload["id_number"]
    student_object = Student.objects.filter(
                                        first_name=student[0],
                                        last_name=student[-1],
                                        _id=id_num)
    if student_object.exists():
        student_object = student_object[0]
    else:
        return redirect("home")

    check = CheckIn.objects.filter(user=student_object,
                                    is_on_clock=True)
    if check.exists():
        check = check[0]
        check.auto_time_out = datetime.now()
        check.time_out = payload['time_out'] if payload['time_out'] != "" else None
        check.is_on_clock = False
        check.save()
    else:
        check = CheckIn(user=student_object,
                        time_in=payload['time_in'] if payload['time_in'] != "" else None,
                        is_on_clock=True)
        check.save()
    async_to_sync(channel_layer.group_send)('events',
        {"type" : "send_message",
         "event" : "websocket.update_students",
         "message" : ",".join([f"{model.user}" for model in CheckIn.objects.filter(is_on_clock=True)])
         })
    return render(request,"checkLanding.html",{"student" : student_object, "status" : check})

@csrf_exempt
@require_POST
def getStudentId(request):
    """
    Private API used by checkin app webdriver to sign-in/out students.
    @param request : http post request

    request body should contain two parameters, 
        first_name key mapped to a str first name
        last_name key mapped to a str last name 
    @return
        a json object with one key "id_number" contaning a 8 digit id number 
    """
    payload = json.loads(request.body)
    student = Student.objects.filter(
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name")
    )
    if student.exists():
        student = student[0]
        return JsonResponse({"id_number" : student._id},status=200)
    else:
        return JsonResponse({"id_number" : "00000000"})

@deprecated
@require_POST
def getAvailableStudents(request):
    """
    Returns a json object with one key "students" which is mapped
    to a list of student names that are on clock.
    """
    students = CheckIn.objects.filter(is_on_clock=True)
    students_on_clock = [str(student) for student in students]
    return JsonResponse({"students" : students_on_clock})


def handle404(request,exception):
    """

    Error 404 Page Handler

    """
    return render(request,'handler.html',{
        'status_code' : 404
    })

def handle500(request):
    """

    Error 500 Page Handler
    
    """
    return render(request,'handler.html',{
        'status_code' : 500
    })