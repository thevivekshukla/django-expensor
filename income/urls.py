from django.conf.urls import url

from . import views

app_name = 'income'



urlpatterns = [
    url(r'^list/$', views.IncomeList.as_view(), name='income-list'),
    url(r'^add/$', views.IncomeAdd.as_view(), name='add-income'),
    url(r'^autocomplete/source/$', views.SourceView.as_view(), name='get-source'),
    url(r'^update/(?P<pk>\d+)/$', views.IncomeUpdateView.as_view(), name='update-income'),
    url(r'^income-search/$', views.IncomeDateSearch.as_view(), name='search'),
]