
from django.urls import (
    include, re_path,
    path,
)
from django.conf.urls import (
    handler403, handler404, handler500
)
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from expense import views

urlpatterns = [
    re_path('django-admin/', admin.site.urls),
    re_path(r'^account/', include('account.urls')),
    re_path(r'^', include('expense.urls')),
    re_path(r'^income/', include('income.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_DIR, document_root=settings.STATIC_ROOT)


handler404 = views.Error404.as_view()
handler500 = views.handler500
handler400 = views.Error400.as_view()
handler403 = views.Error403.as_view()