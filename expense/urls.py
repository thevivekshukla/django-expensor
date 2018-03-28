from django.conf.urls import url

from . import views


app_name = 'expense'


urlpatterns = [
        url(r'^update/(?P<id>\d+)/$', views.update_expense, name='update_expense'),
        url(r'^search/$', views.search, name='search'),
        url(r'^(?P<year>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        url(r'^(?P<year>\d+)/(?P<month>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        url(r'^autocomplete/get_remark/$', views.GetRemark.as_view(), name='get_remark'),
        url(r'^list/$', views.expense_list, name='expense_list'),
        url(r'^day-wise-expense/$', views.DayWiseExpense.as_view(), name='day-wise-expense'),
        url(r'^months/$', views.MonthWiseExpense.as_view(), name='month-wise-expense'),
        url(r'^years/$', views.GetYear.as_view(), name='years'),
        url(r'^$', views.AddExpense.as_view(), name='add_expense'),
]
