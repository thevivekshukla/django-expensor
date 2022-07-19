from datetime import timedelta

from django import template

from utils import helpers
from utils.constants import SHOW_INCOME_CALCULATOR_HOUR

register = template.Library()


@register.filter(name='show_calculator')
def show_calculator(income_object):
    if income_object.amount == 0:
        return False
    now = helpers.get_ist_datetime()
    later_created_time = income_object.created_at \
                            + timedelta(hours=SHOW_INCOME_CALCULATOR_HOUR)
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


@register.simple_tag(name='multiply')
def multiply(v1, v2, round_to=2, multiples_of=None, *args, **kwargs):
    res = round(v1 * v2, round_to)
    res = int(res) if round_to == 0 else res

    if multiples_of:
        res = (res // multiples_of) * multiples_of
    
    return f'{res:,}'

