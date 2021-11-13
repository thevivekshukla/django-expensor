from datetime import timedelta

from django import template

from utils import helpers

register = template.Library()


@register.filter(name='show_calculator')
def show_calculator(income_object):
    now = helpers.get_ist_datetime()
    later_created_time = income_object.created_at + timedelta(days=2)
    if now < later_created_time:
        return True
    return False


@register.simple_tag(name='get_percent')
def get_percent(amount, total):
    return int(round((amount/total) * 100, 0))


