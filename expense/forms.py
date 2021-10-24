from datetime import date

from django import forms
from utils.helpers import get_ist_datetime, default_date_format


class ExpenseForm(forms.Form):
    amount = forms.IntegerField(help_text=" ")
    remark = forms.CharField(required=False,
                widget=forms.TextInput(attrs={'class': 'lowercase_field'}))
    timestamp = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = default_date_format(get_ist_datetime())


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
        today = get_ist_datetime()
        self.fields['from_date'].initial = default_date_format(date(today.year, 1, 1))
        self.fields['to_date'].initial = default_date_format(today)


