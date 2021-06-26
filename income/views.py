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
    SavingCalculatorForm, SavingCalculationModelForm,
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
        qs = Income.objects.filter(user=self.request.user)\
                .order_by('-timestamp', '-created_at',)
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
            messages.success(request, "Income added successfully!")
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
        context = self.context.copy()
        range_form = self.range_form_class(request.GET or None)

        if range_form.is_valid():
            source = range_form.cleaned_data.get('source')
            f_dt = range_form.cleaned_data.get('from_date')
            t_dt = range_form.cleaned_data.get('to_date')
            objects = Income.objects.filter(user=request.user).filter(timestamp__range=(f_dt, t_dt))

            if source:
                objects = objects.filter(source__name__icontains=source)

            object_total = objects.aggregate(Sum('amount'))['amount__sum'] or 0

            context['objects'] = objects
            context['object_total'] = object_total

        context['range_form'] = range_form
        return render(request, self.template_name, context)


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
            cleaned_data = form.cleaned_data
            if instance is None:
                SavingCalculation.objects.create(user=request.user, **cleaned_data)
            else:
                SavingCalculation.objects.filter(user=request.user).update(**cleaned_data)
            messages.success(request, "Savings settings saved successfully!")
        context['form'] = form
        return render(request, self.template_name, context)


class SavingsCalculatorView(View):
    form_class = SavingCalculatorForm
    template_name = "savings-calculator.html"
    context = {
        'title': 'Savings Calculator',
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def return_in_100s(self, amount):
        multiples_of = 100
        mul = amount // multiples_of
        final_amount = int(mul * multiples_of)
        return final_amount

    def get(self, request, *args, **kwargs):
        income = int(request.GET.get('income', 0))
        initial_data = {}

        try:
            savings = request.user.saving_calculation
            initial_data['savings_min_amount'] = savings.savings_min_amount
            initial_data['savings_max_amount'] = savings.savings_max_amount
            initial_data['savings_percentage'] = savings.savings_percentage
            initial_data['debt_percentage'] = savings.debt_percentage
            initial_data['equity_percentage'] = savings.equity_percentage
            initial_data['amount_to_keep_in_bank'] = savings.amount_to_keep_in_bank

            if income:
                initial_data['savings_min_amount'] = self.return_in_100s(income * 0.25)
                initial_data['savings_max_amount'] = self.return_in_100s(income)
                initial_data['amount_to_keep_in_bank'] = self.return_in_100s(income * 0.90)

        except SavingCalculation.DoesNotExist:
            pass

        form = self.form_class(initial=initial_data)
        context = self.context.copy()
        context['form'] = form
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            savings_percentage = form.cleaned_data['savings_percentage']/100
            savings_min_amount = form.cleaned_data['savings_min_amount']
            savings_max_amount = form.cleaned_data['savings_max_amount']
            debt_percentage = form.cleaned_data['debt_percentage']/100
            equity_percentage = form.cleaned_data['equity_percentage']/100
            amount_to_keep_in_bank = form.cleaned_data['amount_to_keep_in_bank']
            bank_balance = form.cleaned_data['bank_balance']

            diff = max(bank_balance - amount_to_keep_in_bank, 0)
            
            if savings_max_amount == 0:
                savings_max_amount = diff

            max_savings = min(diff * savings_percentage, savings_max_amount)
            if max_savings < savings_min_amount:
                diff_savings = diff - savings_min_amount
                if diff_savings > 0:
                    diff = diff_savings
                    to_savings = savings_min_amount
                else:
                    to_savings = diff
                    diff = 0
            else:
                diff -= max_savings
                to_savings = max_savings

            debt = diff * debt_percentage
            equity = diff * equity_percentage

            data = {
                'savings': self.return_in_100s(to_savings),
                'investment': {},
            }
            if debt_percentage:
                data['investment']['debt'] = self.return_in_100s(debt)
            if equity_percentage:
                data['investment']['equity'] = self.return_in_100s(equity)

            context['data'] = data
            context['investment_total'] = sum(value for _, value in data['investment'].items())
            context['total'] = data['savings'] + context['investment_total']

        context['form'] = form
        return render(request, self.template_name, context)




