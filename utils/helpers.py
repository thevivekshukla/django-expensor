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


def get_expense_ratio(user):
    from income.models import Income
    from expense.models import Expense

    income_sum = user.incomes.aggregate(Sum('amount')).get('amount__sum', 0)
    expense_sum = user.expenses.aggregate(Sum('amount')).get('amount__sum', 0)
    
    if income_sum > 0:
        return round(expense_sum/income_sum, 4) * 100
    return None

