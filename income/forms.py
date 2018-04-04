from django import forms
from datetime import timedelta, date



class IncomeForm(forms.Form):
    amount = forms.IntegerField()
    source = forms.CharField(max_length=30, required=False)
    timestamp = forms.DateField()
    class Meta():
        
        fields = ['amount', 'source', 'timestamp']


class SelectDateRangeIncomeForm(forms.Form):
    source = forms.CharField(required=False)
    from_date = forms.DateField(initial=date.today()-timedelta(days=30))
    to_date = forms.DateField(initial=date.today())
