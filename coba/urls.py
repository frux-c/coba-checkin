from django.urls import path,include
from .views import CheckInView,acceptCheckForm,checkInWebhook, checkOutWebhook, getStudentId
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",CheckInView.as_view(),name="home"),
    path("acceptCheckIn/",acceptCheckForm, name="CheckIn"),
    path("webhooks/checkout/",checkOutWebhook, name="CheckOutWebhook"),
    path("webhooks/idnumbers/",getStudentId,name="studentid"),
    path("webhooks/checkin/",checkInWebhook,name="CheckInWebhook"),
]
urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
