from django.urls import re_path
from coba.consumers import CheckInConsumer

websocket_urlpatterns = [
	re_path(r"ws/",CheckInConsumer.as_asgi()),
]