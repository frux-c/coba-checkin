from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import CheckInAPI, CheckInView, StudentsAPI

router = routers.DefaultRouter()
router.register('students', StudentsAPI)
router.register('checkins', CheckInAPI)

urlpatterns = [
    path("",CheckInView.as_view(),name="home"),
    path("api/", include(router.urls), name="api"),

]
urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
