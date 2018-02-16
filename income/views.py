from django.shortcuts import render
from django.views.generic import ListView

from .models import Income, Source
# Create your views here.



class IncomeList(ListView):

    template_name = 'income_list.html'
    model = Income
    paginate_by = 15
    context_object_name = 'objects'