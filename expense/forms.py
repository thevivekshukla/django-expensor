from datetime import date, timedelta

from django import forms
from django.utils import timezone

from .models import Expense
from utils.helpers import get_ist_datetime


class ExpenseForm(forms.Form):
    amount = forms.IntegerField()
    remark = forms.CharField(required=False)
    timestamp = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = get_ist_datetime().date()

    # def clean_timestamp(self, *args, **kwargs):
    #    timestamp = self.cleaned_data.get('timestamp')
    #    today = date.today()
        # three_day = today - timedelta(days=3)
        # ten_day = today - timedelta(days=10)
    #    thirty_day = today - timedelta(days=30)

    #    if timestamp > today:
    #        raise forms.ValidationError("Date cannot be set in future.")

    #    if timestamp < thirty_day:
    #        raise forms.ValidationError("Date cannot be set more than 30 days in past.")

    #   return timestamp



class SelectDateExpenseForm(forms.Form):
    remark = forms.CharField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'remark',
        })
    )
    date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = get_ist_datetime().date()


class SelectDateRangeExpenseForm(forms.Form):
    remark = forms.CharField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'remark',
        })
    )
    from_date = forms.DateField()
    to_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today_date = get_ist_datetime().date()
        self.fields['from_date'].initial = today_date - timedelta(days=30)
        self.fields['to_date'].initial = today_date
