import json
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from .models import Student, CheckIn
from datetime import datetime, timedelta
from datetime import date
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from channels.layers import get_channel_layer  # channel websocket import
from asgiref.sync import async_to_sync, sync_to_async
from rest_framework import viewsets, views, authentication, permissions, renderers
from .serializers import CheckInSerializer, StudentSerializer
from .consumers import CheckInConsumer

# Create your views here.
class CheckInView(TemplateView):
    # write detailed a pydoc for this method
    """
    CheckInView : View for the home page
    """
    template_name = "home.html"
    
    # handle context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get todays records only
        context["students"] = [
            student.user.first_name + " " + student.user.last_name for student in CheckIn.objects.filter(is_on_clock=True, date_created=datetime.now())
            ]
        return context


class CheckInAPI(viewsets.ModelViewSet):
    """

    CheckInViewSet : Rest API for CheckIn Model

    """

    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    permission_classes = [permissions.BasePermission]
    http_method_names = ["get", "post"]

    # handle get request
    def list(self, request, *args, **kwargs):
        # handle the request object
        payload = request.data or request.GET.dict()
        time_stamp = datetime.now()
        if payload:
            if payload.get("on_clock"):
                response = CheckInSerializer(data=self.queryset.filter(
                    is_on_clock=bool(payload.get("on_clock")), date_created=time_stamp), many=True)
        else:
            # get todays records only
            response = CheckInSerializer(data=self.queryset.filter(
                date_created=time_stamp), many=True)
        response.is_valid()
        return JsonResponse({"checkins": response.data})
    

    # handle post request
    def create(self, request, *args, **kwargs):
        # handle the request object
        try:
            payload = json.loads(request.data)
        except TypeError:
            payload = request.data
        except json.JSONDecodeError:
            payload = request.POST.dict()
        print(payload)
        checkin_type = payload.get("type")
        student = None
        if checkin_type == "form":
            full_name = payload.get("student_name").split(" ")
            fname = full_name[0]
            lname = full_name[-1]
            _id = payload.get("student_id")
            if Student.objects.filter(
                first_name=fname, last_name=lname, _id=_id
            ).exists():
                student = Student.objects.get(first_name=fname, last_name=lname, _id=_id)
            else:
                return JsonResponse({"message": "No matching user found"}, status=404)
        if checkin_type == "nfc":
            faculty_code = payload.get("faculty_code")
            card_number = payload.get("card_number")
            if Student.objects.filter(
                card__faculty__code=faculty_code, card__card_number=card_number
            ).exists():
                student = Student.objects.get(
                    card__faculty__code=faculty_code, card__card_number=card_number
                )
            else:
                return JsonResponse({"message": "No matching user found"}, status=404)
        # check if the student is already on the clock
        existing_checkin = CheckIn.objects.filter(user=student, is_on_clock=True).first()
        time_stamp = datetime.now()
        if existing_checkin:
            # checkout the student
            existing_checkin.is_on_clock = False
            existing_checkin.auto_time_out = time_stamp
            existing_checkin.save()
            # announce the student has been checked out
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                CheckInConsumer.GROUP_NAME,
                {
                    "type": "send_group_message",
                    "message": f"{student.first_name} {student.last_name} has checked out",
                    "event": "websocket.checkout",
                },
            )
        else:
            # checkin the student
            checkin = CheckIn.objects.create(user=student)
            checkin.is_on_clock = True
            checkin.auto_time_in = time_stamp
            checkin.save()
            # announce the student has been checked in
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                CheckInConsumer.GROUP_NAME,
                {
                    "type": "send_group_message",
                    "message": f"{student.first_name} {student.last_name} has checked in",
                    "event": "websocket.checkin",
                },
            )
        # announce client to update the students list
        async_to_sync(channel_layer.group_send)(
            CheckInConsumer.GROUP_NAME,
            {
                "type": "send_group_message",
                "message": StudentSerializer([
                    checkin.user for checkin in CheckIn.objects.filter(is_on_clock=True, date_created=time_stamp)
                    ], many=True).data,
                "event": "websocket.update_students",
            },
        )
        return JsonResponse({"message": "Student has checked in", "check_in" : True}, status=201)


class StudentsAPI(viewsets.ModelViewSet):
    """
    StudentViewSet : Rest API for Student Model
    """
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [renderers.JSONRenderer]
    http_method_names = ["get"]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    # handle get request
    def list(self, request, *args, **kwargs):
        # handle the request object
        response = StudentSerializer(data=self.queryset, many=True)
        response.is_valid()
        return JsonResponse({"students": response.data})

class TemplateErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)  # get response from the request
        status_code = response.status_code
        if status_code >= 404: 
            return render(request, "error_middleware_handler.html", {"status_code": response.status_code})
        return response
