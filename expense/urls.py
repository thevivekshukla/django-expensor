from django.conf.urls import url

from . import views


app_name = 'expense'


urlpatterns = [
        url(r'^update/(?P<id>\d+)/$', views.UpdateExpense.as_view(), name='update_expense'),
        url(r'^search/$', views.DateSearch.as_view(), name='search'),

        url(r'^(?P<year>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        url(r'^(?P<year>\d+)/remark/$', views.GoToRemarkWiseExpense.as_view(), name='goto_year_expense'),

        url(r'^(?P<year>\d+)/(?P<month>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        url(r'^(?P<year>\d+)/(?P<month>\d+)/remark/$', views.GoToRemarkWiseExpense.as_view(), name='remark_monthly_expense'),

        url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/remark/$', views.GoToRemarkWiseExpense.as_view(), name='goto_day_expense'),

        url(r'^autocomplete/get_remark/$', views.GetRemark.as_view(), name='get_remark'),
        url(r'^list/$', views.ExpenseList.as_view(), name='expense_list'),
        url(r'^day-wise-expense/$', views.DayWiseExpense.as_view(), name='day-wise-expense'),
        url(r'^months/$', views.MonthWiseExpense.as_view(), name='month-wise-expense'),
        url(r'^years/$', views.GetYear.as_view(), name='years'),
        url(r'^$', views.AddExpense.as_view(), name='add_expense'),
]
