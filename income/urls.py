from django.conf.urls import url

from . import views

app_name = 'income'



urlpatterns = [
    url('^list/$', views.IncomeList.as_view(), name='income-list'),
]