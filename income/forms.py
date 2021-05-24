from typing import Dict, Any

from datetime import timedelta
from django import forms
from django.utils import timezone
from .models import SavingCalculation


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


def validate_percentage(cleaned_data):
    savings_pct = cleaned_data['savings_percentage']
    gold_pct = cleaned_data['gold_percentage']
    debt_pct = cleaned_data['debt_percentage']
    equity_pct = cleaned_data['equity_percentage']

    if not (savings_pct >= 0 and savings_pct <= 100):
        raise forms.ValidationError("Savings percentage should be in between 0 to 100.")

    if sum([gold_pct, debt_pct, equity_pct]) != 100:
        raise forms.ValidationError("Sum of Gold, Debt and Equity percentage fields must be 100")

    return cleaned_data


class SavingCalculationModelForm(forms.ModelForm):
    class Meta:
        model = SavingCalculation
        exclude = (
            'user',
        )

    def clean(self) -> Dict[str, Any]:
        return validate_percentage(super().clean())


class SavingCalculationForm(forms.Form):
    savings_percentage = forms.IntegerField(initial=50, min_value=0, max_value=100)
    savings_min_amount = forms.IntegerField(initial=0)
    savings_max_amount = forms.IntegerField(initial=15000)
    gold_percentage = forms.IntegerField(initial=20, max_value=100)
    debt_percentage = forms.IntegerField(initial=0)
    equity_percentage = forms.IntegerField(initial=50)
    salary_received = forms.IntegerField(label='Salary Received / Amount to keep in Bank')
    bank_balance = forms.IntegerField()

    def clean(self) -> Dict[str, Any]:
        return validate_percentage(super().clean())
        

