from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import CheckInsAPI, CheckInsView, EmployeesAPI

router = routers.DefaultRouter()
router.register('employees', EmployeesAPI)
router.register('checkins', CheckInsAPI)

urlpatterns = [
    path("",CheckInsView.as_view(),name="home"),
    path("api/", include(router.urls), name="api"),

]
urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
