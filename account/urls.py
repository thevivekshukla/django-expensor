from django.urls import re_path

from . import views


app_name = 'account'



urlpatterns = [
        re_path(r'^register/$', views.user_register, name='register'),
        re_path(r'^login/$', views.user_login, name='login'),
        re_path(r'^logout/$', views.user_logout, name='logout'),
        re_path(r'^change-password/$', views.ChangePassword.as_view(), name='change-password'),
        
        re_path(r'^net-worth/$', views.NetWorthDashboard.as_view(), name='networth-dashboard'),
        re_path(r'^net-worth/history/$', views.NetWorthHistoryView.as_view(), name='networth-history'),
        re_path(r'^net-worth/accounts/$', views.AccountNameListView.as_view(), name='account-name-list'),
        re_path(r'^net-worth/accounts/create/$', views.AccountNameCreateView.as_view(), name='account-name-create'),
        re_path(r'^net-worth/accounts/(?P<pk>\d+)/$', views.AccountNameUpdateView.as_view(), name='account-name-update'),
        re_path(r'^net-worth/accounts/(?P<pk>\d+)/delete/$', views.AccountNameDeleteView.as_view(), name='account-name-delete'),
        re_path(r'^net-worth/accounts/(?P<pk>\d+)/amount/$', views.AccountNameAmountAddView.as_view(), name='account-name-amount'),
        re_path(r'^net-worth/accounts/(?P<pk>\d+)/amount/history/$', views.AccountNameAccountHistory.as_view(), name='account-name-amount-history'),
]

