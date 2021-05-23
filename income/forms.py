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


class SavingCalculationModelForm(forms.ModelForm):
    class Meta:
        model = SavingCalculation
        exclude = (
            'user',
        )

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        savings_pct = cleaned_data['savings_percentage']
        gold_pct = cleaned_data['gold_percentage']
        debt_pct = cleaned_data['debt_percentage']
        equity_pct = cleaned_data['equity_percentage']
        if sum([savings_pct, gold_pct, debt_pct, equity_pct]) != 100:
            raise forms.ValidationError("Sum of all percentage fields must be 100")
        return cleaned_data


class SavingCalculationForm(forms.Form):
    savings_min_amount = forms.IntegerField(initial=0)
    savings_max_amount = forms.IntegerField(initial=15000)
    savings_percentage = forms.IntegerField(initial=50, max_value=100)
    gold_percentage = forms.IntegerField(initial=20, max_value=100)
    debt_percentage = forms.IntegerField(initial=0)
    equity_percentage = forms.IntegerField(initial=50)
    salary_received = forms.IntegerField()
    bank_balance = forms.IntegerField()

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        savings_pct = cleaned_data['savings_percentage']
        gold_pct = cleaned_data['gold_percentage']
        debt_pct = cleaned_data['debt_percentage']
        equity_pct = cleaned_data['equity_percentage']
        if sum([savings_pct, gold_pct, debt_pct, equity_pct]) != 100:
            raise forms.ValidationError("Sum of all percentage fields must be 100")
        return cleaned_data

