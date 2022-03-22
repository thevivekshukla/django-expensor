import pytz
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings


def get_ist_datetime(dt=None):
    """
    pass tzinfo aware datetime object i.e. timezone.now()
    """
    if dt is None:
        dt = timezone.now()
    tz = pytz.timezone('Asia/Kolkata')
    return dt.astimezone(tz)


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

