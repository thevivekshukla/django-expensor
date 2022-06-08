from datetime import timedelta
from django import template
from utils import helpers

register = template.Library()


@register.simple_tag(name='multiply')
def multiply(v1, v2, round_to=2, multiples_of=None, *args, **kwargs):
    res = round(v1 * v2, round_to)
    res = int(res) if round_to == 0 else res

    if multiples_of:
        res = (res // multiples_of) * multiples_of
    
    return f'{res:,}'


@register.simple_tag(name='divide')
def divide(v1, v2, round_to=2, *args, **kwargs):
    res = round(v1 / v2, round_to)
    res = int(res) if round_to == 0 else res
    return f'{res:,}'


