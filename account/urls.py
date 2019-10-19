from django.conf.urls import url

from . import views


app_name = 'account'



urlpatterns = [
        url(r'^register/$', views.user_register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        url(r'^change-password/$', views.ChangePassword.as_view(), name='change-password'),
        url(r'^table/$', views.Table.as_view(), name='table'),
]
