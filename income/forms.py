from django import forms
from datetime import timedelta, date



class IncomeForm(forms.Form):
    amount = forms.IntegerField()
    source = forms.CharField(max_length=30, required=False)
    timestamp = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = date.today()
        
    class Meta():
        fields = ['amount', 'source', 'timestamp']


class SelectDateRangeIncomeForm(forms.Form):
    source = forms.CharField(required=False)
    from_date = forms.DateField(initial=date.today()-timedelta(days=365))
    to_date = forms.DateField(initial=date.today())


class SavingsCalculationForm(forms.Form):
    savings_percentage = forms.IntegerField(initial=50)
    savings_max_amount = forms.IntegerField(initial=15000)
    gold_percentage = forms.IntegerField(initial=20)
    # equity_percentage = forms.IntegerField(initial=50)
    salary_received = forms.IntegerField()
    bank_balance = forms.IntegerField()
