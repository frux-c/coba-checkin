from django.urls import path,include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",ServicePage.as_view(),name="home"),
    path("case/<str:slug>/",CasePage.as_view(),name="case"),
    path("case/<str:slug>/add/",addTaskToService,name='add')
]
# urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
