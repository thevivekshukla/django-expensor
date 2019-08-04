from django.contrib import admin

# Register your models here.
from .models import Expense, Remark

admin.site.register(Expense)
admin.site.register(Remark)