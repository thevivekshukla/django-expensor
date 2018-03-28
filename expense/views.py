from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.views import View
from django.views.generic import ListView
from django.utils.decorators import method_decorator

from datetime import date, timedelta
import json

from .forms import ExpenseForm, SelectDateExpenseForm, SelectDateRangeExpenseForm
from .models import Expense

# Create your views here.



@login_required
def add_expense(request):

    form = ExpenseForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            # messages.success(request, "Expense successfully added.")
            # form = ExpenseForm()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)

    context = {
        "title": "Add expense",
        "form": form,
    }

    return render(request, "add_expense.html", context)


@login_required
def update_expense(request, id):
    # instance = get_object_or_404(Expense, id=id)
    instance = Expense.objects.all(user=request.user).filter(id=id).first()

    if instance.user != request.user:
        raise Http404

    # three_day = date.today() - timedelta(days=3)
    thirty_day = date.today() - timedelta(days=30)
    if not instance.timestamp >= thirty_day:
        return HttpResponse("Too late! Cannot be changed now.", status=400)

    form = ExpenseForm(request.POST or None, instance=instance)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Expense successfully updated.")
        form = ExpenseForm()

    context = {
        "title": "Update expense",
        "form": form,
    }

    return render(request, "update_expense.html", context)




@login_required
def expense_list(request):
    objects_list = Expense.objects.all(user=request.user)
    first_date = None

    if objects_list:
        first_date = objects_list.last().timestamp or None

    q = request.GET.get("q")
    object_total = None
    if q:
        objects_list = objects_list.filter(
                    Q(remark__icontains=q) |
                    Q(amount__icontains=q)
                    ).distinct()
        object_total = objects_list.aggregate(Sum('amount'))['amount__sum']

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

    return render(request, "expense_list.html", context)


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

    @method_decorator(login_required)
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

    @method_decorator(login_required)
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


@login_required
def search(request):
    date_form = SelectDateExpenseForm(request.POST or None)
    range_form = SelectDateRangeExpenseForm(request.POST or None)

    objects = None

    if range_form.is_valid():
        f_dt = range_form.cleaned_data.get('from_date')
        t_dt = range_form.cleaned_data.get('to_date')
        objects = Expense.objects.all(user=request.user).filter(timestamp__range=(f_dt, t_dt))

    if date_form.is_valid():
        dt = date_form.cleaned_data.get('date')
        objects = Expense.objects.all(user=request.user).filter(timestamp=dt)

    if objects:
        object_total = objects.aggregate(Sum('amount'))['amount__sum']
    else:
        object_total = None

    context = {
        "title": "Search",
        "date_form": date_form,
        "range_form": range_form,
        "objects": objects,
        "object_total": object_total,
    }

    return render(request, "search.html", context)


@login_required
def goto_expense(request, year=None, month=None, day=None):
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

    return render(request, "goto.html", context)



class GetRemark(View):
    """
    will be used to autocomplete the remarks
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            q = request.GET.get('term', '')
            remarks = Expense.objects.all(user=request.user).filter(remark__icontains=q).order_by(
                      ).values_list('remark', flat=True).distinct()
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
    
    @method_decorator(login_required)
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