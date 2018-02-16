from django import forms



class IncomeForm(forms.Form):
    amount = forms.IntegerField()
    source = forms.CharField(max_length=30)
    timestamp = forms.DateField()
    class Meta():
        
        fields = ['amount', 'source', 'timestamp']