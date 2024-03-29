from django.urls import re_path

from . import views

app_name = 'income'



urlpatterns = [
    re_path(r'^list/$', views.IncomeList.as_view(), name='income-list'),
    re_path(r'^list/year/$', views.YearWiseIncome.as_view(), name='year-income-list'),
    re_path(r'^list/month/$', views.MonthWiseIncome.as_view(), name='month-income-list'),
    re_path(r'^list/month/(?P<year>\d+)/(?P<month>\d+)/$', views.GoToIncome.as_view(), name='goto-income-list'),
    re_path(r'^add/$', views.IncomeAdd.as_view(), name='add-income'),
    re_path(r'^autocomplete/source/$', views.SourceView.as_view(), name='get-source'),
    re_path(r'^source-wise/$', views.SourceWiseIncome.as_view(), name='source-wise'),
    re_path(r'^update/(?P<pk>\d+)/$', views.IncomeUpdateView.as_view(), name='update-income'),
    re_path(r'^income-search/$', views.IncomeDateSearch.as_view(), name='search'),
    
    re_path(r'^report/$', views.YearlyIncomeExpenseReport.as_view(), name='report'),
    re_path(r'^report/(?P<year>\d+)/$', views.MonthlyIncomeExpenseReport.as_view(), name='yearly-report'),
    
    re_path(r'^savings-calculator/settings/$', views.SavingCalculationDetailView.as_view(), name='savings-calculation-detail'),
    re_path(r'^savings-calculator/(?P<income>[\w,]+)?[/]?$', views.SavingsCalculatorView.as_view(), name='savings-calculator'),

    re_path(r'^investment/create/$', views.InvestmentEntityCreateView.as_view(), name='investment-entity-create'),
    re_path(r'^investment/list/$', views.InvestmentEntityListView.as_view(), name='investment-entity-list'),
    re_path(r'^investment/(?P<pk>\d+)/$', views.InvestmentEntityUpdateView.as_view(), name='investment-entity-update'),
    re_path(r'^investment/(?P<pk>\d+)/delete/$', views.InvestmentEntityDeleteView.as_view(), name='investment-entity-delete'),
]

