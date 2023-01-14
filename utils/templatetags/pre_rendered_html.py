from django import template
from django.utils.safestring import mark_safe
from utils import helpers

register = template.Library()


@register.simple_tag(name="past_days_search")
def past_days_search():
    html = ['<ul class="pager">']
    for days in [30, 90, 180, 365]:
        html.append(
            f'<li><a href="?from_date={helpers.timedelta_now_str(days-1)}'
            f'&to_date={helpers.timedelta_now_str(0)}">{days}</a></li>'
        )
    html.append('</ul>')
    return mark_safe("\n".join(html))


