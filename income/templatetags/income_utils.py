from datetime import timedelta, timezone

from django.utils import timezone
from django import template

register = template.Library()


@register.filter(name='show_calculator')
def show_calculator(income_object):
    now = timezone.now()
    later_created_time = income_object.created_at + timedelta(days=1)
    if now < later_created_time:
        return True
    return False