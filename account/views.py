from contextlib import suppress
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DeleteView

from utils.helpers import (
    aggregate_sum,
    cal_avg_expense,
    cal_networth_x,
    calculate_cagr,
    fetch_year_expenses,
    get_client_ip,
    get_ist_datetime,
    get_paginator_object,
)

from .forms import (
    AccountNameAmountForm,
    AccountNameCreateForm,
    ChangePasswordForm,
    LoginForm,
    RegisterUserForm,
)
from .models import AccountName, AccountNameAmount, NetWorth

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
            cache.set(ip_address, invalid_login_count + 1, 3600 * 6)
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
        self.context["form"] = self.form_class()
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
            context["form"] = form
        return render(request, self.template_name, context)


"""
********************* Networth **************************
"""


class NetWorthDashboard(LoginRequiredMixin, View):
    template_name = "networth.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        prev_updated_date = get_ist_datetime() - timedelta(days=90)
        networths = user.net_worth.order_by("-date")
        networth = networths.first()

        if networth:
            avg_expense = cal_avg_expense(user)
            x = cal_networth_x(networth.amount, avg_expense)
        else:
            x = avg_expense = 0

        liabilities = []
        assets = []
        liability_amount = 0
        asset_amount = 0
        account_names = user.account_names.all()
        for account in account_names:
            amount = account.amounts.order_by("-date").first()
            data = {
                "account_name": account,
                "amount": amount.amount if amount and amount.amount else 0,
                "updated": True if amount.created_at >= prev_updated_date else False,
            }
            if account.type == 0:
                liabilities.append(data)
                liability_amount += amount.amount if amount else 0
            else:
                assets.append(data)
                asset_amount += amount.amount if amount else 0

        total_saved_amount = aggregate_sum(user.incomes) - aggregate_sum(user.expenses)
        # lambda function to sort by amount value
        desc_amount_sort = lambda li: sorted(
            li, key=lambda x: x["amount"], reverse=True
        )

        context = {
            "title": "NetWorth",
            "networth": networth,
            "avg_expense": avg_expense,
            "x": x,
            "liabilities": desc_amount_sort(liabilities),
            "liability_amount": liability_amount,
            "assets": desc_amount_sort(assets),
            "asset_amount": asset_amount,
            "total_saved_amount": total_saved_amount,
        }
        return render(request, self.template_name, context)


class NetworthXView(LoginRequiredMixin, View):
    template_name = "networth_x.html"

    def fetch_networth_x(self, method, networth_amount, year_expense):
        month_expense = year_expense // 12
        data = {
            "method": method,
            "year_expense": year_expense,
            "month_expense": month_expense,
            "year_x": cal_networth_x(networth_amount, year_expense),
            "month_x": cal_networth_x(networth_amount, month_expense),
        }
        return data

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            networth_amount = int(request.GET["amount"].replace(",", ""))
        except (ValueError, KeyError):
            networths = user.net_worth.order_by("-date")
            networth = networths.first()
            networth_amount = networth.amount

        data = []
        last_12m_expense = cal_avg_expense(user, YEARS=1)
        year_expenses = fetch_year_expenses(user, YEARS=3)
        
        for method in ["mean", "median", "max", "min"]:
            expense = cal_avg_expense(
                user,
                method=method,
                year_expenses=year_expenses,
            )
            if expense == last_12m_expense:
                method += " (last 12 months')"
            nw_data = self.fetch_networth_x(
                method,
                networth_amount,
                expense,
            )
            data.append(nw_data)

        mean_month_expense = data[0]["month_expense"]
        emergency_fund = mean_month_expense * 6

        fire_amount = mean_month_expense * 12 * 30  # 30 years expenses
        fire_amount_coverage = networth_amount / fire_amount

        fat_fire_amount = mean_month_expense * 12 * 100  # 100 years expenses
        fat_fire_coverage = networth_amount / fat_fire_amount

        context = {
            "title": "Networth X",
            "data": data,
            "networth_amount": networth_amount,
            "emergency_fund": emergency_fund,
            "fire_amount": fire_amount,
            "fire_amount_coverage": fire_amount_coverage,
            "fat_fire_amount": fat_fire_amount,
            "fat_fire_coverage": fat_fire_coverage,
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
            "title": "NetWorth",
            "objects": objects,
            "is_paginated": True,
            "history_cagr": history_cagr,
        }
        return render(request, self.template_name, context)


class AccountNameListView(LoginRequiredMixin, View):
    template_name = "account_name_list.html"

    def get(self, request, *args, **kwargs):
        account_names = request.user.account_names.all()
        liabilities = account_names.filter(type=0)
        assets = account_names.filter(type=1)
        context = {
            "title": "Accounts",
            "liabilities": liabilities,
            "assets": assets,
        }
        return render(request, self.template_name, context)


class AccountNameCreateView(LoginRequiredMixin, View):
    template_name = "account_name_create.html"
    form_class = AccountNameCreateForm
    context = {"title": "Add Account"}

    def get(self, request, *args, **kwargs):
        context = self.context.copy()
        context["form"] = self.form_class()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            account_name = form.save(commit=False)
            account_name.user = request.user
            account_name.save()
            messages.success(request, "New account added!")
            return HttpResponseRedirect(reverse("account:account-name-list"))

        context["form"] = form
        return render(request, self.template_name, context)


class AccountNameUpdateView(LoginRequiredMixin, View):
    template_name = "account_name_create.html"
    form_class = AccountNameCreateForm
    context = {}

    def get_object(self):
        pk = self.kwargs.get("pk")
        account_name = get_object_or_404(AccountName, id=pk)
        self.context["title"] = f"{account_name.name}"
        return account_name

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        context = self.context.copy()
        context["form"] = self.form_class(instance=instance)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        context = self.context.copy()
        form = self.form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Account updated!")
            return HttpResponseRedirect(reverse("account:account-name-list"))

        context["form"] = form
        return render(request, self.template_name, context)


class AccountNameDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountName
    success_url = reverse_lazy("account:account-name-list")
    template_name = "entity-delete.html"
    extra_context = {
        "title": "Confirm Delete",
        "success_url": success_url,
    }

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AccountNameAmountAddView(LoginRequiredMixin, View):
    template_name = "account_name_amount.html"
    form_class = AccountNameAmountForm
    context = {}

    def get_object(self):
        pk = self.kwargs.get("pk")
        account_name = get_object_or_404(AccountName, id=pk)
        self.context["title"] = f"{account_name.name}"
        return account_name

    def get(self, request, *args, **kwargs):
        account_name = self.get_object()
        context = self.context.copy()
        amounts = account_name.amounts.order_by("-date").first()
        if amounts:
            amount = amounts.amount
        else:
            amount = None
        context["form"] = self.form_class()
        context["amount"] = amount
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        account_name = self.get_object()
        context = self.context.copy()
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            data = {
                "account_name": account_name,
                "date": get_ist_datetime().date(),
            }
            account_name_amount = AccountNameAmount.objects.filter(**data).first()
            if account_name_amount:
                account_name_amount.amount = amount
                account_name_amount.save()
            else:
                AccountNameAmount.objects.create(amount=amount, **data)
            messages.success(request, "Account updated!")
            return HttpResponseRedirect(reverse("account:networth-dashboard"))

        context["form"] = form
        return render(request, self.template_name, context)


class AccountNameAccountHistory(LoginRequiredMixin, View):
    template_name = "networth_history.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = AccountName.objects.get(id=pk)
        history = instance.amounts.all().order_by("-date")
        latest_amount = None

        if instance.type == 1 and history.exists():
            latest = history.first()
            start = history.last()
            years = (latest.date - start.date).days / 365
            latest_amount = latest.amount
            history_cagr = calculate_cagr(latest_amount, start.amount, years)
            x = cal_networth_x(latest_amount, cal_avg_expense(request.user))
        else:
            history_cagr = x = 0

        objects = get_paginator_object(request, history, 25)
        context = {
            "title": f"{instance.name} ({instance.get_type_display()})",
            "objects": objects,
            "is_paginated": True,
            "latest_amount": latest_amount,
            "history_cagr": history_cagr,
            "x": x,
        }
        return render(request, self.template_name, context)
