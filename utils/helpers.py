import pytz
from django.utils import timezone
from django.db.models import Sum


def get_ist_datetime(dt=None):
    """
    pass tzinfo aware datetime object i.e. timezone.now()
    """
    if dt is None:
        dt = timezone.now()
    tz = pytz.timezone('Asia/Kolkata')
    return dt.astimezone(tz)


def calculate_ratio(amount, total):
    if total > 0:
        ratio = (amount/total) * 100
        return round(ratio, 2)
    return 0


def expense_to_income_ratio(user):
    expense_sum = user.expenses.aggregate(Sum('amount')).get('amount__sum', 0)
    income_sum = user.incomes.aggregate(Sum('amount')).get('amount__sum', 0)
    return calculate_ratio(expense_sum, income_sum)
    

