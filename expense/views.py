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

from datetime import date, timedelta
import json

from .forms import ExpenseForm, SelectDateExpenseForm, SelectDateRangeExpenseForm
from .models import Expense, Remark
from decorators import login_required_message

# Create your views here.



class AddExpense(View):
    form_class = ExpenseForm
    template_name = "add_expense.html"
    context = {
        'form': form_class,
        'title': "Add expense"
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        last_10_expenses = Expense.objects.all(user=request.user).order_by(
                            '-created_at', '-timestamp',
                        )[:10]
        self.context['objects'] = last_10_expenses
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            remark = form.cleaned_data.get('remark', '').title()
            timestamp = form.cleaned_data.get('timestamp')

            expense = Expense.objects.create(
                user = request.user,
                amount = amount,
                timestamp = timestamp
            )

            if remark:
                try:
                    rem = Remark.objects.get(user=request.user, name=remark)
                except:
                    rem = Remark.objects.create(user=request.user, name=remark)
                expense.remark = rem
                expense.save()
            

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)



class UpdateExpense(View):
    form_class = ExpenseForm
    template_name = "update_expense.html"
    context = {
        "title": "Update expense"
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, request, *args, **kwargs):
        id = int(kwargs['id'])
        instance = Expense.objects.all(user=request.user).filter(id=id).first()

        if not instance:
            raise Http404
        return instance

    def get(self, request, *args, **kwargs):
        instance = self.get_object(request, *args, **kwargs)

        # thirty_day = date.today() - timedelta(days=30)
        # if not instance.timestamp >= thirty_day:
        #     return HttpResponse("<h3>Too late! Cannot be changed now.</h3>", status=400)

        initial_data = {
            'amount': instance.amount,
            'remark': instance.remark,
            'timestamp': instance.timestamp
        }
        form = self.form_class(initial=initial_data)
        self.context['form'] = form
        return render(request, self.template_name, self.context)


    def post(self, request, *args, **kwargs):
        instance = self.get_object(request, *args, **kwargs)

        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            remark = form.cleaned_data.get('remark', '').title()
            timestamp = form.cleaned_data.get('timestamp')

            instance.amount = amount
            instance.timestamp = timestamp
            rem = None
            if remark:
                try:
                    rem = Remark.objects.get(user=request.user, name=remark)
                except:
                    rem = Remark.objects.create(user=request.user, name=remark)
            
            instance.remark = rem
            instance.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)



class ExpenseList(View):
    template_name = "expense_list.html"

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def get(self, request, *args, **kwargs):
        objects_list = Expense.objects.all(user=request.user)
        first_date = None

        if objects_list:
            first_date = objects_list.last().timestamp or None

        q = request.GET.get("q")
        object_total = None
        if q:
            objects_list = objects_list.filter(
                        Q(remark__name__icontains=q) |
                        Q(amount__icontains=q)
                        ).distinct()
            object_total = objects_list.aggregate(Sum('amount'))['amount__sum']

        order_field = request.GET.get("field")
        if order_field:
            ordering = request.GET.get("order", "")+order_field
            print(ordering)
            objects_list = objects_list.order_by(ordering)

        paginator = Paginator(objects_list, 15)

        page = request.GET.get('page')

        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)

        total = Expense.objects.amount_sum(user=request.user)

        context = {
            "title": "Expenses",
            "objects": objects,
            "total": total,
            "first_date": first_date,
            "object_total": object_total,
        }

        return render(request, self.template_name, context)


# class DayWiseExpense(ListView):

#     template_name = "day-expense.html"
#     paginate_by = 30

#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def get_queryset(self, *args, **kwargs):
#         return Expense.objects.all(user=self.request.user).dates('timestamp', 'day').order_by('-timestamp')

#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         queryset = self.get_queryset()
#         days = queryset
#         data = []
#         for day in days:
#             sum_day = queryset.filter(timestamp=day).aggregate(Sum('amount'))['amount__sum']
#             data.append((day, sum_day))
        
#         context['data'] = data
#         context['title'] = 'Day Wise Expense'
#         return context



class DayWiseExpense(View):

    template_name = "day-expense.html"
    context = {
        'title': 'Day Wise Expense',
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        expense = Expense.objects.all(user=request.user)
        days = expense.dates('timestamp', 'day').order_by('-timestamp')
        data = []
        for day in days:
            sum_day = expense.filter(timestamp=day).aggregate(Sum('amount'))['amount__sum']
            data.append((day, sum_day))
        
        self.context['data'] = data
        return render(request, self.template_name, self.context)



class MonthWiseExpense(View):
    template_name = "month-expense.html"
    context = {
        'title': 'Monthly Expense',
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        dates = Expense.objects.all(user=request.user).dates('timestamp', 'month')
        data = []
        for date in dates:
            amount = Expense.objects.this_month(
                user=request.user, year=date.year, month=date.month
                ).aggregate(Sum('amount'))['amount__sum']
            data.append((date, amount))
        self.context['data'] = data
        return render(request, self.template_name, self.context)



class DateSearch(View):
    date_form_class = SelectDateExpenseForm
    range_form_class = SelectDateRangeExpenseForm
    template_name = "search.html"
    context = {
        "title": "Search"
    }

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.context['date_form'] = self.date_form_class()
        self.context['range_form'] = self.range_form_class()

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        date_form = self.date_form_class(request.POST)
        range_form = self.range_form_class(request.POST)

        objects = None

        if range_form.is_valid():
            remark = range_form.cleaned_data.get('remark')
            f_dt = range_form.cleaned_data.get('from_date')
            t_dt = range_form.cleaned_data.get('to_date')
            objects = Expense.objects.all(user=request.user).filter(timestamp__range=(f_dt, t_dt))
            if remark:
                objects = objects.filter(remark__name__icontains=remark)
        else:
            range_form = self.range_form_class()

        if date_form.is_valid():
            remark = date_form.cleaned_data.get('remark')
            dt = date_form.cleaned_data.get('date')
            objects = Expense.objects.all(user=request.user).filter(timestamp=dt)
            if remark:
                objects = objects.filter(remark__name__icontains=remark)
        else:
            date_form = self.date_form_class()

        if objects:
            object_total = objects.aggregate(Sum('amount'))['amount__sum']
        else:
            object_total = None

        
        self.context['date_form'] = date_form
        self.context['range_form'] = range_form
        self.context['objects'] = objects
        self.context['object_total'] = object_total

        return render(request, self.template_name, self.context)



class GoToExpense(View):
    """
    provies expenses for particular day, month or year.
    """
    template_name = 'goto.html'

    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        day = kwargs.get('day')
        month = kwargs.get('month')
        year = kwargs.get('year')
        
        if day:
            objects = Expense.objects.this_day(user=request.user, year=year, month=month, day=day)
        elif month:
            objects = Expense.objects.this_month(user=request.user, year=year, month=month)
        elif year:
            objects = Expense.objects.this_year(user=request.user, year=year)

        goto_total = objects.aggregate(Sum('amount'))['amount__sum']

        paginator = Paginator(objects, 50)

        page = request.GET.get('page')

        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)

        context = {
            "title": "Expenses",
            "objects": objects,
            "goto_total": goto_total,
        }

        return render(request, self.template_name, context)



class GetRemark(View):
    """
    will be used to autocomplete the remarks
    """
    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            q = request.GET.get('term', '')
            # remarks = Expense.objects.all(user=request.user).filter(remark__icontains=q).order_by(
            #           ).values_list('remark', flat=True).distinct()
            remarks = Remark.objects.filter(user=request.user).filter(name__icontains=q).order_by(
                        ).values_list('name', flat=True)
            results = []
            for remark in remarks:
                remark_json = {}
                remark_json['value'] = remark
                results.append(remark_json)
            data = json.dumps(results)
        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)



class GetYear(View):
    """
    return all the year in which expenses are registered.
    """
    @method_decorator(login_required_message)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        cache_key = 'expense_year'
        cache_time = 15768000 # 182.5 days
        data = cache.get(cache_key)

        if not data:
            years = Expense.objects.all(user=request.user).dates('timestamp', 'year')
            result = []

            for y in years:
                result.append(y.year)
            data = json.dumps(result)

        cache.set(cache_key, data, cache_time)

        return HttpResponse(data, content_type='application/json')



class Error404(View):
    def get(self, request, *args, **kwargs):
        return render(request, "404.html", {})


class Error500(View):
    def get(self, request, *args, **kwargs):
        return render(request, "500.html", {})


class Error400(View):
    def get(self, request, *args, **kwargs):
        return render(request, "400.html", {})


class Error403(View):
    def get(self, request, *args, **kwargs):
        return render(request, "403.html", {})