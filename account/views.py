from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import RegisterUserForm, LoginForm

# Create your views here.



def user_register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("expense:expense_list"))

    form = RegisterUserForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        password = form.cleaned_data.get("password")
        instance.set_password(password)
        instance.save()
        return HttpResponseRedirect(reverse("account:login"))

    context = {
        "title": "Register",
        "form": form,
    }

    return render(request, "account_form.html", context)




def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("expense:add_expense"))

    form = LoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if user.is_active:
            if user.is_authenticated():
                login(request, user)
                next_ = request.GET.get("next")
                if next_:
                    return redirect(next_)
                return HttpResponseRedirect(reverse("expense:add_expense"))

    context = {
        "title": "Login",
        "form": form,
    }

    return render(request, "account_form.html", context)






def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("account:login"))
