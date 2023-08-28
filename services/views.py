from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from .models import *
# Create your views here.
class ServicePage(TemplateView):
    template_name='home_page.html'

    def get_context_data(self, **kwargs):
        kwargs["cases"] = ServiceCase.objects.all()
        return super().get_context_data(**kwargs)

class CasePage(DetailView):
    template_name = 'detail_page.html'
    model = ServiceCase
    query_pk_and_slug = True
    def get_context_data(self, **kwargs):
        
        return super().get_context_data(**kwargs)

def addTaskToService(request,slug):
    service = get_object_or_404(ServiceCase,slug=slug)
    payload = request.POST.dict()
    print(payload)
    return render(request,'task_form.html')