from datetime import date

from django import forms
from django.conf import settings
from .models import SavingCalculation

from utils.helpers import get_ist_datetime, default_date_format


class IncomeForm(forms.Form):
    amount = forms.IntegerField(help_text=" ")
    source = forms.CharField(max_length=30, required=False)
    timestamp = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].initial = default_date_format(get_ist_datetime())
        
    class Meta():
        fields = ['amount', 'source', 'timestamp']


class SelectDateRangeIncomeForm(forms.Form):
    source = forms.CharField(required=False)
    from_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    to_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = get_ist_datetime()
        self.fields['from_date'].initial = default_date_format(date(today.year, 1, 1))
        self.fields['to_date'].initial = default_date_format(today)


class SavingCalculationModelForm(forms.ModelForm):
    class Meta:
        model = SavingCalculation
        fields = (
            'message',
            'amount_to_keep_in_bank',
            'auto_fill_amount_to_keep_in_bank',
            'savings_min_amount',
            'auto_fill_savings_min_amount',
            'savings_percentage',
        )
        widgets = {
            'message': forms.Textarea(attrs={'rows':10,}),
            'savings_min_amount': forms.NumberInput(attrs={'placeholder': 'amount', 'min': 0}),
            'savings_percentage': forms.NumberInput(attrs={'placeholder': '(0-100)%', 'min': 0, 'max': 100}),
            'amount_to_keep_in_bank': forms.NumberInput(attrs={'placeholder': 'amount', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auto_fill_amount_to_keep_in_bank'].help_text = "only works if Amount to keep in bank is 0"
        self.fields['auto_fill_savings_min_amount'].help_text = "only works if Savings min amount is 0"


class InvestmentEntityForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.original_data = kwargs.get('data', dict()).copy()
        super().__init__(*args, **kwargs)

        if user:
            try:
                investments = user.saving_calculation.investment_entity.all()
                for inv in investments:
                    self.fields[inv.name] = forms.IntegerField(
                        initial=inv.percentage, min_value=0, max_value=100,
                        widget=forms.NumberInput(attrs={'placeholder': '(0-100)%'}),
                        label=inv.name,
                    )
            except SavingCalculation.DoesNotExist:
                pass

    def clean(self):
        inv_keys = self.fields.keys()
        total = sum(
            int(pct)
            for name, pct in self.original_data.items()
            if name in inv_keys
        )
        if not total in {0, 100}:
            raise forms.ValidationError("Sum of all percentage fields must be either 0 or 100")
        return self.cleaned_data


class SavingCalculatorForm(forms.Form):
    common_amt_widget = forms.NumberInput(attrs={'placeholder': 'amount'})

    bank_balance = forms.IntegerField(min_value=0, widget=common_amt_widget)
    amount_to_keep_in_bank = forms.IntegerField(min_value=0, widget=common_amt_widget)
    savings_min_amount = forms.IntegerField(initial=0, min_value=0, widget=common_amt_widget)
    savings_percentage = forms.IntegerField(initial=100, min_value=0, max_value=100,
                             widget=forms.NumberInput(attrs={'placeholder': '(0-100)%'}))



