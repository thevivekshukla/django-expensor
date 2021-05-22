from datetime import timedelta
from django import forms
from django.utils import timezone


class IncomeForm(forms.Form):
    amount = forms.IntegerField()
    source = forms.CharField(max_length=30, required=False)
    timestamp = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = timezone.now().date()
        
    class Meta():
        fields = ['amount', 'source', 'timestamp']


class SelectDateRangeIncomeForm(forms.Form):
    source = forms.CharField(required=False)
    from_date = forms.DateField()
    to_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today_date = timezone.now().date()
        self.fields['from_date'].initial = today_date - timedelta(days=365)
        self.fields['to_date'].initial = today_date


class SavingsCalculationForm(forms.Form):
    savings_percentage = forms.IntegerField(initial=50, max_value=100)
    savings_max_amount = forms.IntegerField(initial=15000)
    gold_percentage = forms.IntegerField(initial=20, max_value=100)
    # equity_percentage = forms.IntegerField(initial=50)
    salary_received = forms.IntegerField()
    bank_balance = forms.IntegerField()

