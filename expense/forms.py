from datetime import timedelta

from django import forms
from django.conf import settings
from utils.helpers import get_ist_datetime, default_date_format


class ExpenseForm(forms.Form):
    amount = forms.IntegerField(help_text=" ",
                widget=forms.NumberInput(attrs={'autofocus': True}))
    remark = forms.CharField(required=False,
                widget=forms.TextInput(attrs={'class': 'lowercase_field'}))
    timestamp = forms.DateField(label='Date', input_formats=settings.DATE_INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = default_date_format(get_ist_datetime())


class SelectDateRangeExpenseForm(forms.Form):
    remark = forms.CharField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'remark lowercase_field',
        })
    )
    from_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, required=False)
    to_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = get_ist_datetime()
        self.fields['from_date'].initial = default_date_format(today - timedelta(days=364))
        self.fields['to_date'].initial = default_date_format(today)


