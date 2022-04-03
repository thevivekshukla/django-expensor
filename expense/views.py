from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.core.cache import cache
from django.views import View
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import date, timedelta
from calendar import monthrange
import json

from .forms import ExpenseForm, SelectDateRangeExpenseForm
from .models import Expense, Remark
from utils import helpers
from utils.helpers import aggregate_sum, default_date_format
from utils.constants import BANK_AMOUNT_PCT, AVG_MONTH_DAYS

# Create your views here.


class AddExpense(LoginRequiredMixin, View):
    form_class = ExpenseForm
    template_name = "add_expense.html"
    context = {
        'form': form_class,
        'title': "Add Expense"
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            remark = form.cleaned_data.get('remark', '').strip()
            timestamp = form.cleaned_data.get('timestamp')

            remark_object = None
            if remark:
                try:
                    remark_object = Remark.objects.get(user=request.user, name__iexact=remark)
                except Remark.DoesNotExist:
                    remark_object = Remark.objects.create(user=request.user, name=remark)

            Expense.objects.create(
                user = request.user,
                amount = amount,
                timestamp = timestamp,
                remark=remark_object,
            )

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class GetBasicInfo(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user
        today = helpers.get_ist_datetime().date()
        data = dict()

        today_expense = aggregate_sum(Expense.objects.this_day(user=user))
        this_month_expense = aggregate_sum(Expense.objects.this_month(user=user))
        
        data['today_expense'] = f"{today_expense:,}"
        data['this_month_expense'] = f"{this_month_expense:,}"
        
        try:
            bank_balance = user.saving_calculation.amount_to_keep_in_bank
            bank_balance_date = today.replace(day=1)
        except:
            bank_balance = 0
            bank_balance_date = None
        
        if not bank_balance:
            incomes = user.incomes.exclude(amount=0)
            last_income_date = incomes.dates('timestamp', 'month', order='DESC').first()
            if last_income_date:
                last_income = incomes.filter(timestamp__year=last_income_date.year, timestamp__month=last_income_date.month)
                bank_balance = aggregate_sum(last_income) * BANK_AMOUNT_PCT
                bank_balance_date = last_income_date
        
        if bank_balance:
            expense_sum = aggregate_sum(user.expenses.filter(timestamp__range=(bank_balance_date, today)))
            data['this_month_eir'] = helpers.calculate_ratio(expense_sum, bank_balance)
            spending_power = max(0, bank_balance - expense_sum)
            data['spending_power'] = f"{int(spending_power):,}"

        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')


class LatestExpenses(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        recent_expenses = Expense.objects.all(user=request.user).order_by(
                            '-created_at', '-timestamp',
                        )[:10]
        data = []
        for expense in recent_expenses:
            data.append({
                "id": expense.id,
                "amount": f"{expense.amount:,}",
                "remark": expense.remark.name if expense.remark else "",
                "timestamp": expense.timestamp.strftime("%d %b, %y")
            })
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')


class UpdateExpense(LoginRequiredMixin, View):
    form_class = ExpenseForm
    template_name = "update_expense.html"
    context = {
        "title": "Update expense"
    }

    def get_object(self, request, *args, **kwargs):
        id = int(kwargs['id'])
        instance = Expense.objects.all(user=request.user).filter(id=id).first()

        if not instance:
            raise Http404
        return instance

    def get(self, request, *args, **kwargs):
        instance = self.get_object(request, *args, **kwargs)

        initial_data = {
            'amount': instance.amount,
            'remark': instance.remark,
            'timestamp': helpers.default_date_format(instance.timestamp),
        }
        form = self.form_class(initial=initial_data)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        instance = self.get_object(request, *args, **kwargs)

        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            remark = form.cleaned_data.get('remark', '').strip()
            timestamp = form.cleaned_data.get('timestamp')

            instance.amount = amount
            instance.timestamp = timestamp
            rem = None
            if remark:
                try:
                    rem = Remark.objects.get(user=request.user, name__iexact=remark)
                except:
                    rem = Remark.objects.create(user=request.user, name=remark)
            
            instance.remark = rem
            instance.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class ExpenseList(LoginRequiredMixin, View):
    template_name = "expense_list.html"

    def get(self, request, *args, **kwargs):
        objects_list = Expense.objects.all(user=request.user).order_by("-timestamp")
        first_date = None

        if objects_list:
            first_date = objects_list.last().timestamp or None

        q = request.GET.get("q")
        object_total = None
        if q:
            objects_list = helpers.search_expense_remark(objects_list, q)
            object_total = objects_list.aggregate(Sum('amount'))['amount__sum'] or 0

        order_field = request.GET.get("field")
        if order_field:
            ordering = request.GET.get("order", "") + order_field
            objects_list = objects_list.order_by(ordering)

        objects = helpers.get_paginator_object(request, objects_list, 30)
        total = Expense.objects.amount_sum(user=request.user)

        context = {
            "title": "Expenses",
            "objects": objects,
            "total": total,
            "first_date": first_date,
            "object_total": object_total,
            "expense_to_income_ratio": helpers.expense_to_income_ratio(request.user),
        }

        return render(request, self.template_name, context)


class DayWiseExpense(LoginRequiredMixin, View):
    template_name = "day-expense.html"

    def get(self, request, *args, **kwargs):
        context = {}
        date_str = ""
        expense = request.user.expenses

        year = int(request.GET.get('year', 0))
        month = int(request.GET.get('month', 0))
        if year or month:
            if year:
                expense = expense.filter(timestamp__year=year)
                date_str = f": {year}"
            if month:
                expense = expense.filter(timestamp__month=month)
                dt = date(year, month, 1)
                date_str = f": {dt.strftime('%B %Y')}"
            
            context['total'] = expense.aggregate(Sum('amount'))['amount__sum'] or 0

        days = expense.dates('timestamp', 'day', order='DESC')
        days = helpers.get_paginator_object(request, days, 50)

        data = []
        for day in days:
            day_sum = aggregate_sum(expense.filter(timestamp=day))
            data.append({
                'day': day,
                'day_sum': day_sum,
            })
        
        context['title'] = f'Day-Wise Expense{date_str}'
        context['data'] = data
        context['objects'] = days
        return render(request, self.template_name, context)


class MonthWiseExpense(LoginRequiredMixin, View):
    template_name = "month-expense.html"

    def get(self, request, *args, **kwargs):
        context = {}
        date_str = ""
        user = request.user
        year = request.GET.get('year')
        expenses = Expense.objects.all(user=user)
        if year:
            expenses = expenses.filter(timestamp__year=int(year))
            context['total'] = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            context['monthly_average'] = context['total'] // 12
            date_str = f": {year}"

        dates = expenses.dates('timestamp', 'month', order='DESC')
        dates = helpers.get_paginator_object(request, dates, 12)

        data = []
        for date in dates:
            month_expense = Expense.objects.this_month(user=user, year=date.year, month=date.month)
            amount = aggregate_sum(month_expense)
            month_income = user.incomes.filter(timestamp__year=date.year, timestamp__month=date.month)
            month_income_sum = aggregate_sum(month_income)
            month_expense_to_income_ratio = helpers.calculate_ratio(amount, month_income_sum)
            data.append({
                'date': date,
                'amount': amount,
                'month_eir': month_expense_to_income_ratio,
            })

        context['title'] = f'Monthly Expense{date_str}'
        context['data'] = data
        context['objects'] = dates
        return render(request, self.template_name, context)


class YearWiseExpense(LoginRequiredMixin, View):
    """
    return all the year in which expenses are registered.
    """
    template_name = "year-expense.html"
    context = {
        'title': 'Yearly Expense',
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        dates = Expense.objects.all(user=user).dates('timestamp', 'year', order='DESC')
        expense_sum = user.expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        income_sum = user.incomes.aggregate(Sum('amount'))['amount__sum'] or 0

        dates = helpers.get_paginator_object(request, dates, 5)

        data = []
        for date in dates:
            year = date.year
            amount = aggregate_sum(Expense.objects.this_year(user=user, year=year))
            year_income_sum = aggregate_sum(user.incomes.filter(timestamp__year=year))
            
            expense_ratio = helpers.calculate_ratio(amount, expense_sum)
            expense_to_income_ratio = helpers.calculate_ratio(amount, income_sum)
            year_expense_to_income_ratio = helpers.calculate_ratio(amount, year_income_sum)
            
            data.append({
                'year': year,
                'amount': amount,
                'monthly_average': amount // 12,
                'year_eir': year_expense_to_income_ratio,
                'eir': expense_to_income_ratio,
                'expense_ratio': expense_ratio,
            })

        self.context['data'] = data
        self.context['objects'] = dates
        return render(request, self.template_name, self.context)


class DateSearch(LoginRequiredMixin, View):
    form_class = SelectDateRangeExpenseForm
    template_name = "expense_search.html"
    context = {
        "title": "Expense: Search"
    }

    def get(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.GET or None)

        if form.is_valid():
            remark = form.cleaned_data.get('remark', '').strip()
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            objects = Expense.objects.all(user=request.user)
            
            if from_date and to_date:
                objects = objects.filter(timestamp__range=(from_date, to_date))
            elif from_date or to_date:
                the_date = from_date or to_date
                objects = objects.filter(timestamp=the_date)
            
            if remark:
                objects = helpers.search_expense_remark(objects, remark)

            total = aggregate_sum(objects)
            try:
                days = (to_date - from_date).days
                months = days / AVG_MONTH_DAYS
                context['monthly_average'] = int(total/months)
            except:
                pass

            context['objects'] = objects
            context['total'] = total

        context['form'] = form

        return render(request, self.template_name, context)


class GoToExpense(LoginRequiredMixin, View):
    """
    provides expenses for particular day, month or year.
    """
    template_name = 'goto.html'

    def get(self, request, *args, **kwargs):
        day = int(kwargs.get('day', 0))
        month = int(kwargs.get('month', 0))
        year = int(kwargs.get('year', 0))
        date_str = ""
        
        if day:
            objects = Expense.objects.this_day(user=request.user, year=year, month=month, day=day)
            dt = date(year, month, day)
            date_str = f': {dt.strftime("%d %b %Y")}'
        elif month:
            objects = Expense.objects.this_month(user=request.user, year=year, month=month)
            dt = date(year, month, 1)
            date_str = f': {dt.strftime("%b %Y")}'
        elif year:
            objects = Expense.objects.this_year(user=request.user, year=year)
            date_str = f': {year}'

        total = objects.aggregate(Sum('amount'))['amount__sum'] or 0
        objects = helpers.get_paginator_object(request, objects, 50)

        context = {
            "title": f"Expenses{date_str}",
            "objects": objects,
            "total": total,
        }

        return render(request, self.template_name, context)


class GoToRemarkWiseExpense(LoginRequiredMixin, View):
    """
    provies expenses for particular day, month or year.
    """
    template_name = 'remark-wise-expenses.html'
    date_form_class = SelectDateRangeExpenseForm

    def get(self, request, *args, **kwargs):
        user = request.user
        day = int(kwargs.get('day', 0))
        month = int(kwargs.get('month', 0))
        year = int(kwargs.get('year', 0))
        date_str = ""
        
        date_form = self.date_form_class(request.GET or None)
        incomes = user.incomes
        
        if day:
            objects = Expense.objects.this_day(user=user, year=year, month=month, day=day)
            incomes = incomes.filter(timestamp__year=year, timestamp__month=month, timestamp__day=day)
            _day = date(year, month, day)
            date_str = f': {_day.strftime("%d %b %Y")}'
        elif month:
            objects = Expense.objects.this_month(user=user, year=year, month=month)
            incomes = incomes.filter(timestamp__year=year, timestamp__month=month)
            _month = date(year, month, 1)
            date_str = f': {_month.strftime("%b %Y")}'
        elif year:
            objects = Expense.objects.this_year(user=user, year=year)
            incomes = incomes.filter(timestamp__year=year)
            date_str = f': {year}'
        elif date_form.is_valid():
            from_date = date_form.cleaned_data.get('from_date')
            to_date = date_form.cleaned_data.get('to_date')
            objects = user.expenses.filter(timestamp__range=(from_date, to_date))
            incomes = incomes.filter(timestamp__range=(from_date, to_date))
            date_str = f': {default_date_format(from_date)} to {default_date_format(to_date)}'
        else:
            objects = Expense.objects.all(user=user)

        objects = objects.select_related('remark')
        remarks = set()
        for instance in objects:
            remarks.add(instance.remark)

        expense_sum = aggregate_sum(objects)
        income_sum = aggregate_sum(incomes)

        remark_data = []
        for remark in remarks:
            amount = aggregate_sum(objects.filter(remark=remark))
            expense_ratio = helpers.calculate_ratio(amount, expense_sum)
            expense_to_income_ratio = helpers.calculate_ratio(amount, income_sum)
            remark_data.append({
                'remark': remark,
                'amount': amount,
                'eir': expense_to_income_ratio,
                'expense_ratio': expense_ratio,
            })

        remark_data = sorted(remark_data, key=lambda x: x['amount'], reverse=True)

        context = {
            "title": f"Remark-Wise Expenses{date_str}",
            "remarks": remark_data,
            "total": expense_sum,
        }

        return render(request, self.template_name, context)


class GetRemark(LoginRequiredMixin, View):
    """
    will be used to autocomplete the remarks
    """

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        remarks = Remark.objects.filter(user=request.user).filter(name__icontains=term)\
                    .values_list('name', flat=True)
        results = [remark for remark in remarks]
        data = json.dumps(results)

        return HttpResponse(data, content_type='application/json')


class Error404(View):
    def get(self, request, *args, **kwargs):
        return render(request, "404.html", {}, status=404)


def handler500(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response


class Error400(View):
    def get(self, request, *args, **kwargs):
        return render(request, "400.html", {}, status=400)


class Error403(View):
    def get(self, request, *args, **kwargs):
        return render(request, "403.html", {}, status=403)

