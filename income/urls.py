from django.conf.urls import url

from . import views

app_name = 'income'



urlpatterns = [
    url('^list/$', views.IncomeList.as_view(), name='income-list'),
    url('^add/$', views.IncomeAdd.as_view(), name='add-income'),
    url('^autocomplete/source/$', views.SourceView.as_view(), name='get-source'),
]