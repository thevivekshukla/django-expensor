from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .forms import RegisterUserForm, LoginForm, ChangePasswordForm

# Create your views here.


def user_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("expense:expense_list"))

    form = RegisterUserForm(request.POST or None)
    if form.is_valid():
        password = form.cleaned_data.get("password")
        instance = form.save(commit=False)
        instance.set_password(password)
        instance.save()
        return HttpResponseRedirect(reverse("account:login"))

    context = {
        "title": "Sign Up",
        "form": form,
    }
    return render(request, "account_form.html", context)


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("expense:add_expense"))

    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            next_ = request.GET.get("next")
            if next_:
                return redirect(next_)
            return HttpResponseRedirect(reverse("expense:add_expense"))
        else:
            messages.warning(request, "Invalid username or password.")

    context = {
        "title": "Login",
        "form": form,
    }
    return render(request, "account_form.html", context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("account:login"))


class ChangePassword(LoginRequiredMixin, View):
    template_name = "account_form.html"
    form_class = ChangePasswordForm
    context = {
        "title": "Change Password",
    }

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.POST)

        if form.is_valid():
            password = form.cleaned_data.get("password")
            new_password = form.cleaned_data.get("new_password")
            user = authenticate(username=request.user.username, password=password)
            if user:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully!")
                form = self.form_class()
            else:
                messages.warning(request, "The password you've entered is wrong!")
                
        else:
            context['form'] = form
        return render(request, self.template_name, context)



