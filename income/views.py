from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.db.models import Sum

import json

from .models import Income, Source, SavingCalculation
from .forms import (
    IncomeForm, SelectDateRangeIncomeForm,
    SavingCalculationForm, SavingCalculationModelForm,
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


class SavingCalculationDetailView(View):
    form_class = SavingCalculationModelForm
    template_name = "savings-calculation-detail.html"
    context = {
        'title': 'Saving Calculation Detail',
    }

    def get(self, request, *args, **kwargs):
        context = self.context.copy()
        try:
            instance = request.user.saving_calculation
        except SavingCalculation.DoesNotExist:
            instance = None
        form = self.form_class(instance=instance)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        try:
            instance = request.user.saving_calculation
        except SavingCalculation.DoesNotExist:
            instance = None
        form = self.form_class(instance=instance, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            if instance is None:
                instance.user = request.user
            instance.save()
            messages.success(request, "Savings settings saved successfully!")
        context['form'] = form
        return render(request, self.template_name, context)


class SavingsCalculationView(View):
    form_class = SavingCalculationForm
    template_name = "savings-calculation.html"
    context = {
        'title': 'Savings Calculation',
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        initial_data = {'salary_received': request.GET.get('salary_received')}
        try:
            savings = request.user.saving_calculation
            initial_data['savings_min_amount'] = savings.savings_min_amount
            initial_data['savings_max_amount'] = savings.savings_max_amount
            initial_data['savings_percentage'] = savings.savings_percentage
            initial_data['gold_percentage'] = savings.gold_percentage
            initial_data['debt_percentage'] = savings.debt_percentage
            initial_data['equity_percentage'] = savings.equity_percentage
        except SavingCalculation.DoesNotExist:
            pass
        form = self.form_class(initial=initial_data)
        context = self.context.copy()
        context['form'] = form
        return render(request, self.template_name, context)

    def return_in_500s(self, amount):
        return amount
        mul = amount // 500
        final_amount = int(mul * 500)
        return final_amount #f'{final_amount:,}'

    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            savings_min_amount = form.cleaned_data['savings_min_amount']
            savings_max_amount = form.cleaned_data['savings_max_amount']
            savings_percentage = form.cleaned_data['savings_percentage']/100
            gold_percentage = form.cleaned_data['gold_percentage']/100
            debt_percentage = form.cleaned_data['debt_percentage']/100
            equity_percentage = form.cleaned_data['equity_percentage']/100
            salary_received = form.cleaned_data['salary_received']
            bank_balance = form.cleaned_data['bank_balance']

            diff = bank_balance - salary_received

            min_savings = max(diff - savings_min_amount, diff)
            max_savings = min(diff * savings_percentage, savings_max_amount)
            pct_savings = diff * savings_percentage
            if min_savings > savings_min_amount and max_savings != 0:
                to_savings = max_savings
            else:
                to_savings = min_savings

            # for_investment = diff - to_savings
            if to_savings == pct_savings:
                gold = diff * gold_percentage
                debt = diff * debt_percentage
                equity = diff * equity_percentage
            else:
                for_investment = diff - to_savings
                gold = for_investment * (gold_percentage/(1-gold_percentage))
                debt = for_investment * (debt_percentage/(1-debt_percentage))
                equity = for_investment * (equity_percentage/(1-equity_percentage))

            data = {
                'savings': self.return_in_500s(to_savings),
                'gold': self.return_in_500s(gold),
                'debt': self.return_in_500s(debt),
                'equity': self.return_in_500s(equity),
            }
            context['data'] = data

        context['form'] = form
        return render(request, self.template_name, context)




