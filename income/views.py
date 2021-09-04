import statistics
from datetime import timedelta
import math

from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView, CreateView,
    UpdateView, DeleteView,
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Sum

import json

from .models import (
    Income, Source,
    SavingCalculation,
    InvestmentEntity,
)
from .forms import (
    IncomeForm, SelectDateRangeIncomeForm,
    SavingCalculatorForm, SavingCalculationModelForm,
    InvestmentEntityForm,
)
from utils import helpers
# Create your views here.



class IncomeList(LoginRequiredMixin, ListView):
    template_name = 'income_list.html'
    paginate_by = 15
    context_object_name = 'objects'

    def get_queryset(self, *args, **kwargs):
        qs = Income.objects.filter(user=self.request.user)\
                .order_by('-timestamp', '-created_at',)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Income List'
        saving_to_income_ratio = 100 - helpers.expense_to_income_ratio(self.request.user)
        context['saving_to_income_ratio'] = round(saving_to_income_ratio, 2)
        return context


class IncomeAdd(LoginRequiredMixin, View):
    template_name = 'add_income.html'
    form_class = IncomeForm

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
            source_name = form.cleaned_data.get('source', '').strip()

            source = None
            if source_name:
                source, _ = Source.objects.get_or_create(user=request.user, name=source_name)

            Income.objects.create(
                    user=request.user,
                    amount=amount,
                    timestamp=timestamp,
                    source=source,
                )
            messages.success(request, "Income added successfully!")
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class IncomeUpdateView(LoginRequiredMixin, View):
    template_name = 'update_income.html'
    form_class = IncomeForm
    context = {
        'title': 'Update Income',
    }

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
            source_name = form.cleaned_data.get('source', '').strip()
            if source_name:
                try:
                    source = Source.objects.get(user=request.user, name=source_name)
                except Source.DoesNotExist:
                    source = Source.objects.create(user=request.user, name=source_name)
                income.source = source

            income.amount = amount
            income.timestamp = timestamp
            income.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class MonthWiseIncome(LoginRequiredMixin, View):
    template_name = "month-income.html"
    context = {
        'title': 'Monthly Income',
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        incomes = Income.objects.filter(user=user)
        dates = incomes.dates('timestamp', 'month')
        data = []

        for date in dates:
            amount = incomes.filter(
                timestamp__year=date.year,
                timestamp__month=date.month,
            ).aggregate(Sum('amount')).get('amount__sum', 0)
            data.append((date, amount))

        self.context['data'] = data
        return render(request, self.template_name, self.context)


class SourceView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        sources = Source.objects.filter(user=request.user, name__icontains=term)\
                    .values_list('name', flat=True)

        result = [source for source in sources]
        data = json.dumps(result)
        
        return HttpResponse(data, content_type='application/json')


class IncomeDateSearch(LoginRequiredMixin, View):
    range_form_class = SelectDateRangeIncomeForm
    template_name = "income-search.html"
    context = {
        "title": "Income: Search"
    }

    def get(self, request, *args, **kwargs):
        context = self.context.copy()
        range_form = self.range_form_class(request.GET or None)

        if range_form.is_valid():
            source = range_form.cleaned_data.get('source').strip()
            f_dt = range_form.cleaned_data.get('from_date')
            t_dt = range_form.cleaned_data.get('to_date')
            objects = Income.objects.filter(user=request.user).filter(timestamp__range=(f_dt, t_dt))

            if source:
                objects = objects.filter(source__name=source)

            object_total = objects.aggregate(Sum('amount'))['amount__sum'] or 0

            context['objects'] = objects
            context['object_total'] = object_total

        context['range_form'] = range_form
        return render(request, self.template_name, context)


class SavingCalculationDetailView(LoginRequiredMixin, View):
    form_class = SavingCalculationModelForm
    inv_form_class = InvestmentEntityForm
    template_name = "savings-calculation-detail.html"
    context = {
        'title': 'Saving Calculation Detail',
    }

    def get(self, request, *args, **kwargs):
        try:
            instance = request.user.saving_calculation
        except SavingCalculation.DoesNotExist:
            instance = None

        context = self.context.copy()
        context['form'] = self.form_class(instance=instance)
        context['inv_form'] = self.inv_form_class(user=request.user)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            instance = request.user.saving_calculation
        except SavingCalculation.DoesNotExist:
            instance = None
        
        form = self.form_class(instance=instance, data=request.POST)
        inv_form = self.inv_form_class(user=request.user, data=request.POST)

        if form.is_valid() and inv_form.is_valid():
            cleaned_data = form.cleaned_data
            inv_cleaned_data = inv_form.cleaned_data
            # updating savings instance
            if instance is None:
                instance = SavingCalculation.objects.create(user=request.user, **cleaned_data)
            else:
                SavingCalculation.objects.filter(user=request.user).update(**cleaned_data)

            # updating investment entity
            for name, pct in inv_cleaned_data.items():
                InvestmentEntity.objects.filter(saving_calculation=instance, name=name)\
                    .update(percentage=pct)
            messages.success(request, "Savings settings saved successfully!")
        else:
            messages.warning(request, "There is some error, please check fields below")

        context = self.context.copy()
        context['form'] = form
        context['inv_form'] = inv_form
        return render(request, self.template_name, context)


class InvestmentEntityCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = "investment-entity-create.html"
    model = InvestmentEntity
    fields = ['name',]
    success_url = reverse_lazy('income:investment-entity-list')
    success_message = "Investment Entity Created"
    extra_context = {
        'title': 'Add Investment Entity',
    }

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.saving_calculation = self.request.user.saving_calculation
        obj.save()
        return super().form_valid(form)


class InvestmentEntityListView(LoginRequiredMixin, ListView):
    template_name = "investment-entity-list.html"
    model = InvestmentEntity
    extra_context = {
        'title': 'Investments List',
    }

    def get_queryset(self):
        return self.model.objects.filter(
            saving_calculation=self.request.user.saving_calculation,
        )


class InvestmentEntityUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = InvestmentEntity
    fields = ['name',]
    template_name = "investment-entity-create.html"
    extra_context = {
        'title': 'Update Investment Entity',
    }
    success_url = reverse_lazy('income:investment-entity-list')
    success_message = "Updated successfully!"

    def get_queryset(self):
        return self.model.objects.filter(
            saving_calculation=self.request.user.saving_calculation,
        )


class InvestmentEntityDeleteView(LoginRequiredMixin, DeleteView):
    model = InvestmentEntity
    success_url = reverse_lazy('income:investment-entity-list')
    template_name = "investment-entity-delete.html"
    extra_context = {
        'title': 'Confirm Delete',
    }

    def get_queryset(self):
        return self.model.objects.filter(
            percentage=0,
            saving_calculation=self.request.user.saving_calculation,
        )


class SavingsCalculatorView(LoginRequiredMixin, View):
    form_class = SavingCalculatorForm
    inv_form_class = InvestmentEntityForm
    template_name = "savings-calculator.html"
    context = {
        'title': 'Savings Calculator',
    }

    def return_in_multiples(self, amount, multiples_of=100):
        amount = math.ceil(amount)
        final_amount = (amount // multiples_of) * multiples_of
        return final_amount

    def gen_bank_amount(self):
        MONTHS = 6
        DAYS = MONTHS * 30
        now = helpers.get_ist_datetime().date()
        past = now - timedelta(days=DAYS)

        incomes = self.request.user.incomes.filter(timestamp__range=(past, now))
        income_sum = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        avg_income = income_sum / MONTHS

        return avg_income

    def get(self, request, *args, **kwargs):
        user = request.user
        income = request.GET.get('income')
        initial_data = {}
        message = None
        defaults_message = []

        try:
            savings = user.saving_calculation
            message = savings.message
            initial_data['savings_min_amount'] = savings.savings_min_amount
            initial_data['savings_percentage'] = savings.savings_percentage
            initial_data['amount_to_keep_in_bank'] = savings.amount_to_keep_in_bank

            MIN_SAVINGS_PCT = 10/100
            BANK_AMOUNT = self.gen_bank_amount()

            if income:
                income = int(income)
                defaults_message.append(f"Income: ₹ {income:,}")

            if not savings.savings_min_amount and savings.auto_fill_savings_min_amount:
                income_to_use = income if income else BANK_AMOUNT
                initial_data['savings_min_amount'] = self.return_in_multiples(income_to_use * MIN_SAVINGS_PCT)
                defaults_message.append("Savings Min Amount used is system generated")
            
            if not savings.amount_to_keep_in_bank and savings.auto_fill_amount_to_keep_in_bank:
                initial_data['amount_to_keep_in_bank'] = self.return_in_multiples(BANK_AMOUNT)
                defaults_message.append(f"Amount To Keep In Bank used is system generated")

        except SavingCalculation.DoesNotExist:
            pass

        context = self.context.copy()
        context['form'] = self.form_class(initial=initial_data)
        context['inv_form'] = self.inv_form_class(user=user)
        context['message'] = message
        context['defaults_message'] = defaults_message
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(data=request.POST)
        inv_form = self.inv_form_class(user=request.user, data=request.POST)

        if form.is_valid() and inv_form.is_valid():
            savings_min_amount = form.cleaned_data['savings_min_amount']
            savings_percentage = form.cleaned_data['savings_percentage']/100
            amount_to_keep_in_bank = form.cleaned_data['amount_to_keep_in_bank']
            bank_balance = form.cleaned_data['bank_balance']
            investment_data = inv_form.cleaned_data

            cal_amount = max(bank_balance - amount_to_keep_in_bank, 0)

            # savings calculation
            savings = max(savings_min_amount, cal_amount * savings_percentage)
            cal_amount -= savings
            if cal_amount < 0:
                savings += cal_amount
                cal_amount = 0

            data = {
                'savings': self.return_in_multiples(savings),
                'investment': {},
            }

            # investment calculation from here
            investment_total = 0
            for inv_name, inv_pct in investment_data.items():
                if inv_pct:
                    inv_amount = self.return_in_multiples(
                        cal_amount * (inv_pct/100)
                    )
                    data['investment'][inv_name] = inv_amount
                    investment_total += inv_amount

            context['data'] = data
            context['investment_total'] = investment_total
            context['total'] = data['savings'] + investment_total
        else:
            messages.warning(request, "There is some error, please check fields below")

        context['form'] = form
        context['inv_form'] = inv_form
        return render(request, self.template_name, context)




