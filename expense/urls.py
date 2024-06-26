from django.urls import re_path

from . import views


app_name = 'expense'


urlpatterns = [
        re_path(r'^update/(?P<id>\d+)/$', views.UpdateExpense.as_view(), name='update_expense'),
        re_path(r'^search/$', views.DateSearch.as_view(), name='search'),

        re_path(r'^all/remark/$', views.GoToRemarkWiseExpense.as_view(), name='all_remark_expenses'),

        re_path(r'^(?P<year>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        re_path(r'^(?P<year>\d+)/remark/$', views.GoToRemarkWiseExpense.as_view(), name='goto_year_expense'),

        re_path(r'^(?P<year>\d+)/(?P<month>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        re_path(r'^(?P<year>\d+)/(?P<month>\d+)/remark/$', views.GoToRemarkWiseExpense.as_view(), name='remark_monthly_expense'),

        re_path(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.GoToExpense.as_view(), name='goto_expense'),
        re_path(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/remark/$', views.GoToRemarkWiseExpense.as_view(), name='goto_day_expense'),

        re_path(r'^autocomplete/get_remark/$', views.GetRemark.as_view(), name='get_remark'),
        re_path(r'^list/$', views.ExpenseList.as_view(), name='expense_list'),
        re_path(r'^day-wise-expense/$', views.DayWiseExpense.as_view(), name='day-wise-expense'),
        re_path(r'^months/$', views.MonthWiseExpense.as_view(), name='month-wise-expense'),
        re_path(r'^years/$', views.YearWiseExpense.as_view(), name='year-wise-expense'),
        re_path(r'^$', views.AddExpense.as_view(), name='add_expense'),

        re_path(r'^basic-info/$', views.GetBasicInfo.as_view(), name='get-basic-info'),
        re_path(r'^latest-expenses/$', views.LatestExpenses.as_view(), name='get-latest-expenses'),
]
