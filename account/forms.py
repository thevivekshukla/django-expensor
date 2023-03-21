from django import forms
from django.contrib.auth import get_user_model

from .models import (
    AccountName,
    AccountNameAmount,
)

User = get_user_model()


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean_username(self, *args, **kwargs):
        return self.cleaned_data.get("username", "").lower()
        
    def clean_email(self, *args, **kwargs):
        return self.cleaned_data.get("email", "").lower()

    def clean_confirm_password(self, *args, **kwargs):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Password does not match.")

        return confirm_password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta():
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'lowercase_field'}),
            'email': forms.EmailInput(attrs={'class': 'lowercase_field'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'lowercase_field'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean_username(self, *args, **kwargs):
        return self.cleaned_data.get("username", "").lower()


class ChangePasswordForm(forms.Form):
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    new_password = forms.CharField(required=True, widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise forms.ValidationError("New password must match.")
        
        return cleaned_data
            

class AccountNameCreateForm(forms.ModelForm):
    class Meta:
        model = AccountName
        fields = [
            'name',
            'type',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True}),
        }
        


class AccountNameAmountForm(forms.Form):
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={'autofocus': True}))

