"""expensor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import (
    url, include, handler400, handler403, handler404, handler500
)
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from expense import views

urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^account/', include('account.urls')),
    url(r'^', include('expense.urls')),
    url(r'^income/', include('income.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_DIR, document_root=settings.STATIC_ROOT)



handler404 = views.Error404.as_view()
handler500 = views.Error500.as_view()
handler400 = views.Error400.as_view()
handler403 = views.Error403.as_view()