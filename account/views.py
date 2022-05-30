from datetime import timedelta
from contextlib import suppress

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache

from .models import (
    AccountName,
    AccountNameAmount,
    NetWorth,
)
from .forms import (
    RegisterUserForm, LoginForm, ChangePasswordForm,
    AccountNameCreateForm, AccountNameAmountForm,
)
from utils.helpers import (
    aggregate_sum,
    get_ist_datetime,
    get_client_ip,
    get_paginator_object,
    calculate_cagr,
)

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
    
    # checking for invalid login count
    ip_address = get_client_ip(request)
    invalid_login_count = cache.get(ip_address, 0)
    if invalid_login_count >= 5:
        return HttpResponse(status=429)

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
            # updating invalid login count
            cache.set(ip_address, invalid_login_count + 1, 3600)
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


"""
********************* Networth **************************
"""

class NetWorthDashboard(LoginRequiredMixin, View):
    template_name = "networth.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        networths = user.net_worth.order_by('-date')
        networth = networths.first()
        
        x = 0
        avg_expense = 0
        if networth and networth.amount > 0:
            YEARS = 5
            expense_months = user.expenses.exclude(amount=0)\
                                .dates('timestamp', 'month', order='DESC')
            expense_sum = 0
            months = min(expense_months.count(), YEARS * 12)
            for dt in expense_months[:months]:
                expense = user.expenses.filter(timestamp__year=dt.year, timestamp__month=dt.month)
                expense_sum += aggregate_sum(expense)
            
            avg_expense = int(expense_sum / (months / 12))
            with suppress(ZeroDivisionError):
                x = round(networth.amount / avg_expense, 1)
        
        liabilities = []
        assets = []
        liability_amount = 0
        asset_amount = 0
        account_names = user.account_names.all()
        for account in account_names:
            amount = account.amounts.order_by('-date').first()
            data = {
                'account_name': account,
                'amount': amount,
            }
            if account.type == 0:
                liabilities.append(data)
                liability_amount += amount.amount if amount else 0
            else:
                assets.append(data)
                asset_amount += amount.amount if amount else 0
        
        context = {
            'title': 'NetWorth',
            'networth': networth,
            'avg_expense': avg_expense,
            'YEARS': YEARS,
            'x': x,
            'liabilities': liabilities,
            'liability_amount': liability_amount,
            'assets': assets,
            'asset_amount': asset_amount,
        }
        return render(request, self.template_name, context)


class NetWorthHistoryView(LoginRequiredMixin, View):
    template_name = "networth_history.html"
    
    def get(self, request, *args, **kwargs):
        networth = NetWorth.objects.filter(user=request.user)
        
        history_cagr = 0
        if networth.exists():
            final = networth.first()
            start = networth.last()
            years = (final.date - start.date).days / 365
            history_cagr = calculate_cagr(final.amount, start.amount, years)
        
        objects = get_paginator_object(request, networth, 25)
        context = {
            'title': 'NetWorth',
            'objects': objects,
            'is_paginated': True,
            'history_cagr': history_cagr,
        }
        return render(request, self.template_name, context)


class AccountNameListView(LoginRequiredMixin, View):
    template_name = "account_name_list.html"

    def get(self, request, *args, **kwargs):
        account_names = request.user.account_names.all()
        liabilities = account_names.filter(type=0)
        assets = account_names.filter(type=1)
        context = {
            'title': 'Accounts',
            'liabilities': liabilities,
            'assets': assets,
        }
        return render(request, self.template_name, context)


class AccountNameCreateView(LoginRequiredMixin, View):
    template_name = "account_name_create.html"
    form_class = AccountNameCreateForm
    context = {'title': 'Add Account'}
    
    def get(self, request, *args, **kwargs):
        context = self.context.copy()
        context['form'] = self.form_class()
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            account_name = form.save(commit=False)
            account_name.user = request.user
            account_name.save()
            messages.success(request, "New account added!")
            return HttpResponseRedirect(reverse('account:account-name-list'))

        context['form'] = form
        return render(request, self.template_name, context)


class AccountNameUpdateView(LoginRequiredMixin, View):
    template_name = "account_name_create.html"
    form_class = AccountNameCreateForm
    context = {}
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        account_name = get_object_or_404(AccountName, id=pk)
        self.context['title'] = f'{account_name.name}'
        return account_name
    
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        context = self.context.copy()
        context['form'] = self.form_class(instance=instance)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        context = self.context.copy()
        form = self.form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Account updated!")
            return HttpResponseRedirect(reverse('account:account-name-list'))

        context['form'] = form
        return render(request, self.template_name, context)
        

class AccountNameDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountName
    success_url = reverse_lazy('account:account-name-list')
    template_name = "entity-delete.html"
    extra_context = {
        'title': 'Confirm Delete',
        'success_url': success_url,
    }

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AccountNameAmountAddView(LoginRequiredMixin, View):
    template_name = "account_name_amount.html"
    form_class = AccountNameAmountForm
    context = {}
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        account_name = get_object_or_404(AccountName, id=pk)
        self.context['title'] = f'{account_name.name}'
        return account_name
    
    def get(self, request, *args, **kwargs):
        account_name = self.get_object()
        context = self.context.copy()
        amounts = account_name.amounts.order_by('-date').first()
        if amounts:
            amount = amounts.amount
        else:
            amount = None
        context['form'] = self.form_class(initial={'amount': amount})
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        account_name = self.get_object()
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            data = {
                'account_name': account_name,
                'date': get_ist_datetime().date(),
            }
            account_name_amount = AccountNameAmount.objects.filter(**data).first()
            if account_name_amount:
                account_name_amount.amount = amount
                account_name_amount.save()
            else:
                AccountNameAmount.objects.create(amount=amount, **data)
            messages.success(request, "Account updated!")
            return HttpResponseRedirect(reverse('account:networth-dashboard'))

        context['form'] = form
        return render(request, self.template_name, context)


class AccountNameAccountHistory(LoginRequiredMixin, View):
    template_name = "networth_history.html"
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = AccountName.objects.get(id=pk)
        history = instance.amounts.all().order_by('-date')
        
        history_cagr = 0
        if history.exists():
            final = history.first()
            start = history.last()
            years = (final.date - start.date).days / 365
            history_cagr = calculate_cagr(final.amount, start.amount, years)
        
        objects = get_paginator_object(request, history, 25)
        context = {
            'title': f'{instance.name} ({instance.get_type_display()})',
            'objects': objects,
            'is_paginated': True,
            'history_cagr': history_cagr,
        }
        return render(request, self.template_name, context)



