from django import forms
from django.utils import timezone

from datetime import date, timedelta


from .models import Expense


class ExpenseForm(forms.ModelForm):

    timestamp = forms.DateField(initial=date.today())

    class Meta():
        model = Expense
        fields = ["amount", "remark", "timestamp"]

    def clean_timestamp(self, *args, **kwargs):
        timestamp = self.cleaned_data.get('timestamp')
        today = date.today()
        # three_day = today - timedelta(days=3)
        # ten_day = today - timedelta(days=10)
        thirty_day = today - timedelta(days=30)

        if timestamp > today:
            raise forms.ValidationError("Date cannot be set in future.")

        if timestamp < thirty_day:
            raise forms.ValidationError("Date cannot be set more than 30 days in past.")

        return timestamp



class SelectDateExpenseForm(forms.Form):
    date = forms.DateField(initial=date.today())


class SelectDateRangeExpenseForm(forms.Form):
    from_date = forms.DateField(initial=date.today()-timedelta(days=30))
    to_date = forms.DateField(initial=date.today())
