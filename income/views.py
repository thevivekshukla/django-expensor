from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.db.models import Sum

import json

from .models import Income, Source
from .forms import (
    IncomeForm, SelectDateRangeIncomeForm,
    SavingsCalculationForm, 
)

from decorators import login_required_message
# Create your views here.



class IncomeList(ListView):

    template_name = 'income_list.html'
    paginate_by = 15
    context_object_name = 'objects'

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = Income.objects.filter(user=self.request.user)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Income List'
        return context


class IncomeAdd(View):

    template_name = 'add_income.html'
    form_class = IncomeForm

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'income_form': self.form_class,
            'title' : 'Add Income',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            timestamp = form.cleaned_data.get('timestamp')
            source_name = form.cleaned_data.get('source')
            if source_name:
                try:
                    source = Source.objects.get(name=source_name, user=request.user)
                except Source.DoesNotExist:
                    source = Source.objects.create(name=source_name, user=request.user)
                income = Income.objects.create(
                    user=request.user,
                    amount=amount,
                    timestamp=timestamp,
                    source=source
                )
            else:
                income = Income.objects.create(
                    user=request.user,
                    amount=amount,
                    timestamp=timestamp
                )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class IncomeUpdateView(View):

    template_name = 'update_income.html'
    form_class = IncomeForm
    context = {
        'title': 'Update Income',
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = int(kwargs['pk'])
        income = get_object_or_404(Income, id=pk, user=request.user)

        #checking if user own the object
        if income.user != request.user:
            raise Http404

        initial_data = {
            'amount': income.amount,
            'source': income.source,
            'timestamp': income.timestamp,
        }
        
        self.context['income_form'] = self.form_class(initial=initial_data)

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        pk = int(kwargs['pk'])
        income = get_object_or_404(Income, id=pk, user=request.user)

        #checking if user own the object
        if income.user != request.user:
            raise Http404

        form = self.form_class(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            timestamp = form.cleaned_data['timestamp']
            source_name = form.cleaned_data.get('source', None)
            if source_name:
                try:
                    source = Source.objects.get(name=source_name, user=request.user)
                except Source.DoesNotExist:
                    source = Source.objects.create(name=source_name, user=request.user)
                income.source = source

            income.amount = amount
            income.timestamp = timestamp
            income.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class SourceView(View):

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        source = Source.objects.filter(name__icontains=term, user=request.user)
        result = []

        for s in source:
            result.append(s.name)
        data = json.dumps(result)
        
        return HttpResponse(data, content_type='application/json')



class IncomeDateSearch(View):
    range_form_class = SelectDateRangeIncomeForm
    template_name = "income-search.html"
    context = {
        "title": "Income: Search"
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.context['range_form'] = self.range_form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        range_form = self.range_form_class(request.POST)

        objects = None

        if range_form.is_valid():
            source = range_form.cleaned_data.get('source')
            f_dt = range_form.cleaned_data.get('from_date')
            t_dt = range_form.cleaned_data.get('to_date')
            objects = Income.objects.filter(user=request.user).filter(timestamp__range=(f_dt, t_dt))
            if source:
                objects = objects.filter(source__name__icontains=source)
        else:
            range_form = self.range_form_class()

        if objects:
            object_total = objects.aggregate(Sum('amount'))['amount__sum']
        else:
            object_total = None

        self.context['range_form'] = range_form
        self.context['objects'] = objects
        self.context['object_total'] = object_total

        return render(request, self.template_name, self.context)


class SavingsCalculationView(View):
    form_class = SavingsCalculationForm
    template_name = "savings-calculation.html"
    context = {
        'title': 'Savings Calculation',
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        salary_received = request.GET.get('salary_received')
        form = self.form_class(initial={'salary_received': salary_received})
        context = self.context.copy()
        context['form'] = form
        return render(request, self.template_name, context)

    def return_in_500s(self, amount):
        mul = amount // 500
        final_amount = int(mul * 500)
        return final_amount #f'{final_amount:,}'

    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            savings_percentage = form.cleaned_data['savings_percentage']/100
            savings_max_amount = form.cleaned_data['savings_max_amount']
            gold_percentage = form.cleaned_data['gold_percentage']/100
            salary_received = form.cleaned_data['salary_received']
            bank_balance = form.cleaned_data['bank_balance']
            equity_percentage = 1 - gold_percentage

            diff = bank_balance - salary_received
            to_savings = min(diff * savings_percentage, savings_max_amount)
            for_investment = diff - to_savings

            gold = for_investment * gold_percentage
            equity = for_investment * equity_percentage

            data = {
                'savings': self.return_in_500s(to_savings),
                'gold': self.return_in_500s(gold),
                'equity': self.return_in_500s(equity),
            }
            context['data'] = data

        context['form'] = form
        return render(request, self.template_name, context)




