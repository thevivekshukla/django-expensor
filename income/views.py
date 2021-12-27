from datetime import timedelta, date
import math
import statistics
import markdown
from collections import Counter

from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
        context['objects'] = context['page_obj']
        context['title'] = 'Income List'
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
            'timestamp': helpers.default_date_format(income.timestamp),
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
        dates = incomes.dates('timestamp', 'month', order='DESC')
        dates = helpers.get_paginator_object(request, dates, 12)

        data = []
        for date in dates:
            amount = incomes.filter(
                timestamp__year=date.year,
                timestamp__month=date.month,
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            data.append((date, amount))

        self.context['data'] = data
        self.context['objects'] = dates
        return render(request, self.template_name, self.context)


class GoToIncome(LoginRequiredMixin, View):
    """
    provides income for particular day, month or year.
    """
    template_name = 'income_list.html'

    def get(self, request, *args, **kwargs):
        month = int(kwargs.get('month', 0))
        year = int(kwargs.get('year', 0))
        date_str = ""
        
        incomes = request.user.incomes.all()
        if year:
            incomes = incomes.filter(timestamp__year=year)
            date_str = f"{year}"
        if year and month:
            incomes = incomes.filter(timestamp__month=month)
            dt = date(year, month, 1)
            date_str = dt.strftime("%B %Y")

        context = {
            "title": f"Income: {date_str}",
            "objects": incomes,
            "total": incomes.aggregate(Sum('amount'))['amount__sum'] or 0,
        }
        return render(request, self.template_name, context)


class SourceView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        sources = Source.objects.filter(user=request.user, name__icontains=term)\
                    .values_list('name', flat=True)

        result = [source for source in sources]
        data = json.dumps(result)
        
        return HttpResponse(data, content_type='application/json')


class IncomeDateSearch(LoginRequiredMixin, View):
    form_class = SelectDateRangeIncomeForm
    template_name = "income-search.html"
    context = {
        "title": "Income: Search"
    }

    def get(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.GET or None)

        if form.is_valid():
            source = form.cleaned_data.get('source').strip()
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            objects = Income.objects.filter(user=request.user)

            if from_date and to_date:
                objects = objects.filter(timestamp__range=(from_date, to_date))
            elif from_date or to_date:
                the_date = from_date or to_date
                objects = objects.filter(timestamp=the_date)

            if source:
                objects = objects.filter(source__name=source)

            object_total = objects.aggregate(Sum('amount'))['amount__sum'] or 0
            try:
                days = (to_date - from_date).days
                months = days / 30
                context['monthly_average'] = int(object_total/months)
            except:
                pass

            context['objects'] = objects
            context['object_total'] = object_total

        context['form'] = form
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

    def return_in_multiples(self, amount):
        user = self.request.user
        try:
            multiples_of = user.saving_calculation.amount_in_multiples_of
        except:
            multiples_of = 100
            
        amount = int(round(amount, 0))
        final_amount = (amount // multiples_of) * multiples_of
        return final_amount

    def gen_bank_amount(self):
        MONTHS = 3
        DAYS = MONTHS * 30
        OFFSET_DAYS = [-15, 0, 15]

        now = helpers.get_ist_datetime().date()
        amounts = []
        incomes = self.request.user.incomes

        for offset_day in OFFSET_DAYS:
            offset_now = now + timedelta(days=offset_day)
            past = offset_now - timedelta(days=DAYS)
            offset_incomes = incomes.filter(timestamp__range=(past, offset_now))
            income_sum = offset_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
            avg_income = income_sum // MONTHS
            amounts.append(avg_income)

        if not amounts:
            return 0

        most_common = Counter(amounts).most_common(1)
        _, count = most_common[0]
        if count > (len(OFFSET_DAYS) // 2):
            return statistics.median(amounts)
        else:
            return statistics.mean(amounts)

    def get(self, request, *args, **kwargs):
        user = request.user
        income = request.GET.get('income')
        initial_data = {}
        message = ""
        defaults_message = []

        try:
            savings = user.saving_calculation
            message = markdown.markdown(savings.message if savings.message else "")
            initial_data['savings_fixed_amount'] = savings.savings_fixed_amount
            initial_data['savings_percentage'] = savings.savings_percentage
            initial_data['amount_to_keep_in_bank'] = savings.amount_to_keep_in_bank

            BANK_AMOUNT_PCT = 80
            FIXED_SAVINGS_PCT = 10
            BANK_AMOUNT = int(self.gen_bank_amount())

            if income:
                income = int(income)
                defaults_message.append(f'Income: <span id="curr_income" class="badge">{income:,}</span>')

            if not savings.amount_to_keep_in_bank and savings.auto_fill_amount_to_keep_in_bank:
                initial_data['amount_to_keep_in_bank'] = self.return_in_multiples(BANK_AMOUNT * (BANK_AMOUNT_PCT/100))
                defaults_message.append(f'Amount to keep in bank is <span id="bank_amount_pct">{BANK_AMOUNT_PCT}</span>% of <span id="bank_amount">{BANK_AMOUNT:,}</span>')

            if not savings.savings_fixed_amount and savings.auto_fill_savings_fixed_amount:
                income_to_use = income if income else BANK_AMOUNT
                initial_data['savings_fixed_amount'] = self.return_in_multiples(income_to_use * (FIXED_SAVINGS_PCT/100))
                defaults_message.append(f"Savings fixed amount is {FIXED_SAVINGS_PCT}% of {income_to_use:,}")

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
            savings_fixed_amount = form.cleaned_data['savings_fixed_amount']
            savings_percentage = form.cleaned_data['savings_percentage']/100
            amount_to_keep_in_bank = form.cleaned_data['amount_to_keep_in_bank']
            bank_balance = form.cleaned_data['bank_balance']
            investment_data = inv_form.cleaned_data

            cal_amount = max(bank_balance - amount_to_keep_in_bank, 0)

            # savings calculation
            savings = savings_fixed_amount
            cal_amount -= savings
            if cal_amount < 0:
                savings += cal_amount
                cal_amount = 0
            else:
                savings_percentage_amount = cal_amount * savings_percentage
                savings += savings_percentage_amount
                cal_amount -= savings_percentage_amount

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




