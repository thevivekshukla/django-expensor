from django.shortcuts import render
from django.views.generic import ListView
from django.views import View

from .models import Income, Source
from .forms import IncomeForm
# Create your views here.



class IncomeList(ListView):

    template_name = 'income_list.html'
    model = Income
    paginate_by = 15
    context_object_name = 'objects'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Income List'
        return context


class IncomeAdd(View):

    template_name = 'add_income.html'
    form_class = IncomeForm

    def get(self, request, *args, **kwargs):

        context = {
            'income_form': self.form_class,
            'title' : 'Add Income',
        }

        return render(request, self.template_name, context)
