from datetime import timedelta
from functools import lru_cache
import statistics

import pytz
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage,
)
from django.conf import settings


def get_ist_datetime(dt=None):
    """
    pass tzinfo aware datetime object i.e. timezone.now()
    """
    if dt is None:
        dt = timezone.now()
    tz = pytz.timezone('Asia/Kolkata')
    return dt.astimezone(tz)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def aggregate_sum(queryset, field_name='amount'):
    return queryset.aggregate(Sum(field_name))[field_name + '__sum'] or 0


def calculate_ratio(amount, total):
    if total > 0:
        ratio = (amount/total) * 100
        return round(ratio, 2)
    return 0


def expense_to_income_ratio(user):
    expense_sum = user.expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    income_sum = user.incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    return calculate_ratio(expense_sum, income_sum)


def get_paginator_object(request, queryset, paginate_by):
    paginator = Paginator(queryset, paginate_by)
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
        
    return objects


def default_date_format(dt):
    return dt.strftime(settings.DEFAULT_DATE_FORMAT)
    

def search_expense_remark(queryset, q):
    filter_Q = Q(amount__iexact=q)
    queries = [x.strip() for x in q.split(',')]

    for query in queries:
        if query.count('"') == 2 and (query[0] == '"' and query[-1] == '"'):
            query = query.strip('"')
            filter_Q |= Q(remark__name__iexact=query)
        else:
            filter_Q |= Q(remark__name__icontains=query)
    
    queryset = queryset.filter(filter_Q).distinct()
    return queryset


@lru_cache(maxsize=128)
def get_dates_list(first_date, latest_date, *, month=None, day=None, daydelta=-1):
    replace_kwargs = dict()
    if month:
        replace_kwargs['month'] = month
    if day:
        replace_kwargs['day'] = day
    
    latest_date = latest_date.replace(**replace_kwargs)
    dates = [latest_date]
    while latest_date > first_date:
        latest_date += timedelta(days=daydelta)
        latest_date = latest_date.replace(**replace_kwargs)
        dates.append(latest_date)
    return dates


def calculate_cagr(final_amount, start_amount, years):
    networth_cagr = 0
    if years:
        if start_amount > 0 and final_amount > 0:
            networth_cagr = (final_amount / start_amount) ** (1 / years) - 1
        elif start_amount < 0 and final_amount < 0:
            networth_cagr = -1 * ((abs(final_amount) / abs(start_amount)) ** (1 / years) - 1)
        elif start_amount < 0 and final_amount > 0:
            networth_cagr = ((final_amount + 2 * abs(start_amount)) / abs(start_amount))  ** (1 / years) - 1
        elif start_amount > 0 and final_amount < 0:
            networth_cagr = -1 * (((abs(final_amount) + 2 * start_amount) / start_amount) ** (1 / years) - 1)
        networth_cagr = round(networth_cagr * 100, 2)
    return networth_cagr


def cal_avg_expense(user, *, method="mean", YEARS=3):
    """
    Returns yearly average expense
    """
    today = get_ist_datetime().date()
    
    latest_month = today.replace(day=1) - timedelta(days=1)
    latest_month = latest_month.replace(day=1)
    first_month = user.expenses.dates('timestamp', 'month', order='ASC').first() or latest_month
    
    months = get_dates_list(first_month, latest_month, day=1)
    year, _ = divmod(min(len(months), YEARS * 12), 12)
    year_expenses = []
    
    for i in range(0, year):
        expenses = 0
        from_range = i * 12
        to_range = (i + 1) * 12
        for dt in months[from_range:to_range]:
            expense = user.expenses.filter(timestamp__year=dt.year, timestamp__month=dt.month)
            expenses += aggregate_sum(expense)
        if expenses:
            year_expenses.append(expenses)

    if not year_expenses:
        return 0
    
    if method == "mean":
        method_func = statistics.mean
    elif method == "median":
        method_func = statistics.median
    elif method == "max":
        method_func = max
    elif method == "min":
        method_func = min
    else:
        raise ValueError("Invalid value provided for 'method' kwarg")

    return int(method_func(year_expenses))


def cal_networth_x(amount, yearly_expense):
    if amount > 0:
        try:
            return round(amount / yearly_expense, 1)
        except ZeroDivisionError:
            pass
    return 0



