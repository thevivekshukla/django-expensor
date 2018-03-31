from django import forms
from django.contrib.auth import (authenticate,
                                login,
                                logout,
                                get_user_model
                                )


User = get_user_model()


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_password2(self, *args, **kwargs):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Password does not match.")

        return password


    class Meta():
        model = User
        fields = ["username", "email", "password", "password2"]





class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self, *args, **kwargs):
        username = self.cleaned_data.get("username")

        if username == '':
            raise forms.ValidationError("Username cannot be blank.")

        user = User.objects.filter(username=username)

        if not user:
            raise forms.ValidationError("User with this username does not exist.")

        return username

    def clean_password(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if password == '':
            raise forms.ValidationError("Password cannot be blank.")

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError("You have entered wrong password.")

        return password


class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput)

    def clean_confirm_new_password(self, *args, **kwargs):
        password = self.cleaned_data.get("new_password")
        password2 = self.cleaned_data.get("confirm_new_password")

        if password != password2:
            raise forms.ValidationError("Password must match.")
        
        return password2
            
