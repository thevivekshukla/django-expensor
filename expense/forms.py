from datetime import date, timedelta

from django import forms
from django.utils import timezone

from .models import Expense
from utils.helpers import get_ist_datetime


class ExpenseForm(forms.Form):
    amount = forms.IntegerField(help_text=" ")
    remark = forms.CharField(required=False,
                widget=forms.TextInput(attrs={'class': 'lowercase_field'}))
    timestamp = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = get_ist_datetime().date()


class SelectDateRangeExpenseForm(forms.Form):
    remark = forms.CharField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'remark lowercase_field',
        })
    )
    from_date = forms.DateField()
    to_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today_date = get_ist_datetime().date()
        self.fields['from_date'].initial = today_date - timedelta(days=30)
        self.fields['to_date'].initial = today_date

