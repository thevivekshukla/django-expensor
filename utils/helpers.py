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


def calculate_expense_ratio(user, expense_amount, income_sum=None):
    if income_sum is None:
        income_sum = user.incomes.aggregate(Sum('amount')).get('amount__sum', 0)
        
    if income_sum > 0:
        ratio = (expense_amount/income_sum) * 100
        return round(ratio, 2)
    return None


def get_expense_ratio(user):
    expense_sum = user.expenses.aggregate(Sum('amount')).get('amount__sum', 0)
    return calculate_expense_ratio(user, expense_sum)
    

