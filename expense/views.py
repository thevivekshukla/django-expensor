from datetime import date
import json
import calendar

from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import HttpResponse, Http404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .forms import ExpenseForm, SelectDateRangeExpenseForm
from .models import Expense, Remark
from income.models import SavingCalculation
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
            bank_balance = user.saving_calculation.amount_to_keep_in_bank * BANK_AMOUNT_PCT
            bank_balance_date = today.replace(day=1)
        except SavingCalculation.DoesNotExist:
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
        objects_list = Expense.objects.all(user=request.user)

        order_field = request.GET.get("field")
        if order_field:
            ordering = request.GET.get("order", "") + order_field
            objects_list = objects_list.order_by(ordering)

        objects = helpers.get_paginator_object(request, objects_list, 30)
        
        # total = Expense.objects.amount_sum(user=request.user)
        # if objects_list:
        #     first_date = objects_list.last().timestamp
        # else:
        #     first_date = None

        context = {
            "title": "Expenses",
            "objects": objects,
            # "total": total,
            # "first_date": first_date,
            # "expense_to_income_ratio": helpers.expense_to_income_ratio(request.user),
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
        now = helpers.get_ist_datetime()
        expenses = Expense.objects.all(user=user)
        
        if year:
            year = int(year)
            total_months = now.month if now.year == year else 12
            expenses = expenses.filter(timestamp__year=year)
            context['total'] = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            context['monthly_average'] = context['total'] // total_months
            date_str = f": {year}"
            context['remark_url'] = reverse('expense:goto_year_expense', kwargs={'year': int(year)})
            context['daywise_url'] = reverse('expense:day-wise-expense') + f'?year={year}'
            alt_first_date = date(year, 1, 1)
            if year == now.year:
                latest_date = date(year, now.month, 1)
            else:
                latest_date = date(year, 12, 1)
        else:
            alt_first_date = now.date().replace(month=1, day=1)
            latest_date = now.date().replace(day=1)
        
        # doing this way to maintain continuity of months
        first_date = expenses.dates('timestamp', 'month', order='ASC').first() or alt_first_date
        dates = helpers.get_dates_list(first_date, latest_date, day=1)
        dates = helpers.get_paginator_object(request, dates, 12)

        data = []
        for dt in dates:
            month_expense = Expense.objects.this_month(user=user, year=dt.year, month=dt.month)
            amount = aggregate_sum(month_expense)
            month_income = user.incomes.filter(timestamp__year=dt.year, timestamp__month=dt.month)
            month_income_sum = aggregate_sum(month_income)
            month_expense_to_income_ratio = helpers.calculate_ratio(amount, month_income_sum)
            data.append({
                'date': dt,
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
        now = helpers.get_ist_datetime()
        expense_sum = user.expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        income_sum = user.incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        
        latest_date = now.date().replace(month=1, day=1)
        first_date = user.expenses.dates('timestamp', 'year', order='ASC').first() or latest_date
        dates = helpers.get_dates_list(first_date, latest_date, month=1, day=1)
        dates = helpers.get_paginator_object(request, dates, 5)
        
        data = []
        for date in dates:
            year = date.year
            total_months = now.month if now.year == year else 12
            amount = aggregate_sum(Expense.objects.this_year(user=user, year=year))
            year_income_sum = aggregate_sum(user.incomes.filter(timestamp__year=year))
            
            expense_ratio = helpers.calculate_ratio(amount, expense_sum)
            expense_to_income_ratio = helpers.calculate_ratio(amount, income_sum)
            year_expense_to_income_ratio = helpers.calculate_ratio(amount, year_income_sum)
            
            data.append({
                'year': year,
                'amount': amount,
                'monthly_average': amount // total_months,
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
        context = dict()
        date_str = ""
        from_date_str = to_date_str = None
        objects = Expense.objects.all(user=request.user)
        
        initial = dict()
        first_expense = objects.exclude(amount=0).order_by('timestamp', 'created_at').first()
        if first_expense:
            initial['from_date'] = default_date_format(first_expense.timestamp)
        form = self.form_class(request.GET or None, initial=initial)

        if form.is_valid():
            remark = form.cleaned_data.get('remark', '').strip()
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            
            if from_date and to_date:
                objects = objects.filter(timestamp__range=(from_date, to_date))
                from_date_str = default_date_format(from_date)
                to_date_str = default_date_format(to_date)
                date_str = f': {from_date_str} to {to_date_str}'
            elif from_date or to_date:
                the_date = from_date or to_date
                objects = objects.filter(timestamp=the_date)
                from_date_str = to_date_str = default_date_format(the_date)
                date_str = f': {from_date_str}'
            
            if remark == '""':
                objects = objects.filter(remark__isnull=True)
            elif remark:
                objects = helpers.search_expense_remark(objects, remark)

            total = aggregate_sum(objects)
            try:
                days = (to_date - from_date).days
                months = days / AVG_MONTH_DAYS
                if months > 1:
                    context['monthly_average'] = int(total/months)
            except:
                pass

            context['objects'] = helpers.get_paginator_object(request, objects, 30)
            context['total'] = total

        context['title'] = f'Expense Search{date_str}'
        context['form'] = form
        context['from_date'] = from_date_str
        context['to_date'] = to_date_str
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
        from_date = to_date = None
        daywise_url_reverse = reverse('expense:day-wise-expense')
        
        if day:
            objects = Expense.objects.this_day(user=request.user, year=year, month=month, day=day)
            dt = date(year, month, day)
            date_str = f': {dt.strftime("%d %b %Y")}'
            remark_url_name = "goto_day_expense"
            daywise_url = ""
            from_date = to_date = default_date_format(dt)
        elif month:
            objects = Expense.objects.this_month(user=request.user, year=year, month=month)
            dt = date(year, month, 1)
            date_str = f': {dt.strftime("%b %Y")}'
            remark_url_name = "remark_monthly_expense"
            daywise_url = f'{daywise_url_reverse}?year={year}&month={month}'
            from_date = default_date_format(date(year, month, 1))
            to_date = default_date_format(
                date(year, month, calendar.monthrange(year, month)[1])
            )
        elif year:
            objects = Expense.objects.this_year(user=request.user, year=year)
            date_str = f': {year}'
            remark_url_name = "goto_year_expense"
            daywise_url = f'{daywise_url_reverse}?year={year}'
            from_date = default_date_format(date(year, 1, 1))
            to_date = default_date_format(date(year, 12, 31))

        total = objects.aggregate(Sum('amount'))['amount__sum'] or 0
        objects = helpers.get_paginator_object(request, objects, 50)

        context = {
            "title": f"Expenses{date_str}",
            "objects": objects,
            "total": total,
            "remark_url": reverse(f'expense:{remark_url_name}',
                            kwargs={k:int(v) for k, v in kwargs.items()}),
            "daywise_url": daywise_url,
            "from_date": from_date,
            "to_date": to_date,
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
        from_date = to_date = None
        objects = user.expenses
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
            from_date = default_date_format(date(year, month, 1))
            to_date = default_date_format(
                date(year, month, calendar.monthrange(year, month)[1])
            )
        elif year:
            objects = Expense.objects.this_year(user=user, year=year)
            incomes = incomes.filter(timestamp__year=year)
            date_str = f': {year}'
            from_date = default_date_format(date(year, 1, 1))
            to_date = default_date_format(date(year, 12, 31))
        elif date_form.is_valid():
            remark = date_form.cleaned_data.get('remark')
            _from_date = date_form.cleaned_data.get('from_date')
            _to_date = date_form.cleaned_data.get('to_date')
            objects = user.expenses
            if _from_date and _to_date:
                objects = objects.filter(timestamp__range=(_from_date, _to_date))
                incomes = incomes.filter(timestamp__range=(_from_date, _to_date))
                from_date = default_date_format(_from_date)
                to_date = default_date_format(_to_date)
                date_str = f': {from_date} to {to_date}'
            if remark:
                objects = helpers.search_expense_remark(objects, remark)

        objects = objects.select_related('remark')
        remarks = set()
        for instance in objects:
            remarks.add(instance.remark)

        expense_sum = aggregate_sum(objects)
        income_sum = aggregate_sum(incomes)

        remark_data = []
        for remark in remarks:
            remark_filter = objects.filter(remark=remark)
            amount = aggregate_sum(remark_filter)
            expense_ratio = helpers.calculate_ratio(amount, expense_sum)
            expense_to_income_ratio = helpers.calculate_ratio(amount, income_sum)
            remark_data.append({
                'remark': remark,
                'remark_count': remark_filter.count(),
                'amount': amount,
                'eir': expense_to_income_ratio,
                'expense_ratio': expense_ratio,
            })

        remark_data = sorted(remark_data, key=lambda x: x['amount'], reverse=True)

        context = {
            "title": f"Remark-Wise Expenses{date_str}",
            "remarks": remark_data,
            "total": expense_sum,
            "from_date": from_date,
            "to_date": to_date,
        }

        return render(request, self.template_name, context)


class GetRemark(LoginRequiredMixin, View):
    """
    will be used to autocomplete the remarks
    """

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip().lower()
        remarks = request.user.remarks
        if len(term) < 3:
            remarks = remarks.filter(name__startswith=term)
        else:
            remarks = remarks.filter(name__icontains=term)
        
        remarks = remarks.annotate(count=Count('expenses'))\
                    .order_by('-count', 'name')
        results = [remark.name for remark in remarks[:10]]
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

