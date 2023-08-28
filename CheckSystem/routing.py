from django.urls import re_path
from coba.consumers import CheckInConsumer

websocket_urlpatterns = [
	re_path(r"",CheckInConsumer.as_asgi()),
]