from django.urls import path
from .views import *

urlpatterns = [
    path("", checkinForm, name="ashkanHome"),
    path("handlecheckin", handle_checkin, name='ashkanHandleCheckin')
]