import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer  # channel websocket import
from django.core.files.storage import FileSystemStorage # TODO : for image proof
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import (authentication, permissions, renderers,viewsets)

from .consumers import CheckInConsumer
from .models import CheckIn, Employee
from .serializers import CheckInSerializer, EmployeeSerializer


# Create your views here.
class CheckInsView(TemplateView):
    # write detailed a pydoc for this method
    """
    CheckInView : View for the home page
    """
    template_name = "home.html"
    
    # handle context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get todays records only
        context["employees"] = [
            employee.employee.first_name + " " + employee.employee.last_name for employee in CheckIn.objects.filter(is_on_clock=True, creation_date=datetime.now())
            ]
        return context


class CheckInsAPI(viewsets.ModelViewSet):
    """

    CheckInViewSet : Rest API for CheckIn Model

    """
    queryset = CheckIn.objects.filter(creation_date=datetime.now())
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
                    is_on_clock=bool(payload.get("on_clock")), creation_date=time_stamp), many=True)
        else:
            # get todays records only
            response = CheckInSerializer(data=self.queryset.filter(
                creation_date=time_stamp), many=True)
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
        checkin_type = payload.get("type")
        if checkin_type == "form":
            full_name = payload.get("employee_name").split(" ", 1)
            fname = full_name[0]
            lname = full_name[-1]
            employee_id = int(payload.get("employee_id"))
            if Employee.objects.filter(
                first_name=fname, last_name=lname, employee_id=employee_id
            ).exists():
                employee = Employee.objects.get(first_name=fname, last_name=lname, employee_id=employee_id)
            else:
                return JsonResponse({"message": "No matching user found"}, status=404)
        elif checkin_type == "nfc":
            faculty_code = payload.get("faculty_code")
            card_number = int(payload.get("card_number"))
            if Employee.objects.filter(
                card__faculty__code=faculty_code, card__card_number=card_number
            ).exists():
                employee = Employee.objects.get(
                    card__faculty__code=faculty_code, card__card_number=card_number
                )
            else:
                return JsonResponse({"message": "No matching user found"}, status=404)
        # check if the employee is already on the clock
        existing_checkin = CheckIn.objects.filter(employee=employee, is_on_clock=True).first()
        time_stamp = datetime.now()
        if existing_checkin:
            # checkout the employee
            CheckIn.objects.filter(id=existing_checkin.id).update(is_on_clock=False, auto_time_out=time_stamp)
            # announce the employee has been checked out
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                CheckInConsumer.GROUP_NAME,
                {
                    "type": "send_group_message",
                    "message": f"{employee.first_name} {employee.last_name} has checked out",
                    "event": "websocket.checkout",
                },
            )
        else:
            # checkin the employee
            CheckIn.objects.create(employee=employee, is_on_clock=True, auto_time_in=time_stamp)
            # announce the employee has been checked in
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                CheckInConsumer.GROUP_NAME,
                {
                    "type": "send_group_message",
                    "message": f"{employee.first_name} {employee.last_name} has checked in",
                    "event": "websocket.checkin",
                },
            )
        # announce client to update the employees list
        async_to_sync(channel_layer.group_send)(
            CheckInConsumer.GROUP_NAME,
            {
                "type": "send_group_message",
                "message": EmployeeSerializer([
                    checkin.employee for checkin in CheckIn.objects.filter(is_on_clock=True, creation_date=time_stamp)
                    ], many=True).data,
                "event": "websocket.update_employees",
            },
        )
        if existing_checkin:
            return JsonResponse({"message": "Student has checked out", "check_in" : False}, status=201)
        return JsonResponse({"message": "Student has checked in", "check_in" : True}, status=201)


class EmployeesAPI(viewsets.ModelViewSet):
    """
    StudentViewSet : Rest API for Student Model
    """
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [renderers.JSONRenderer]
    http_method_names = ["get"]
    serializer_class = EmployeeSerializer
    queryset = Employee.objects

    # handle get request
    def list(self, request, *args, **kwargs):
        # refresh the queryset
        response = EmployeeSerializer(data=self.queryset, many=True)
        response.is_valid()
        return JsonResponse({"employees": response.data})

class TemplateErrorMiddleware:
    """
    TemplateErrorMiddleware : Middleware for handling template errors
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)  # get response from the request
        status_code = response.status_code
        # check for all bad status codes
        client_error_codes = {400, 401, 403, 404, 405, 408, 409, 410, 413, 414, 429}
        server_error_codes = {500, 501, 502, 503, 504, 505, 507, 508, 509, 510, 511}
        if status_code in client_error_codes or status_code in server_error_codes:
            return render(request, "error_middleware_handler.html", {"status_code": response.status_code})
        return response
