from datetime import timedelta

from django import template

from utils import helpers

register = template.Library()


@register.filter(name='show_calculator')
def show_calculator(income_object):
    now = helpers.get_ist_datetime()
    later_created_time = income_object.created_at + timedelta(days=7)
    if now < later_created_time:
        return True
    return False


@register.simple_tag(name='get_percent')
def get_percent(amount, total):
    try:
        return int(round((amount/total) * 100, 0))
    except ZeroDivisionError:
        return 0


@register.filter(name='simplify_amount')
def simplify_amount(amount):
    M = 1_000_000
    K = 1000
    abs_amount = abs(amount)
    
    if abs_amount > M:
        return f"{round(amount/M, 2)}M"
    elif abs_amount > K:
        return f"{int(round(amount/K, 0))}K"
    else:
        return f"{amount}"


