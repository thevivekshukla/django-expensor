from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.conf import settings
from django.db.models.signals import pre_save

from datetime import date

from utils.base_model import BaseModel
from utils.helpers import get_ist_datetime

# Create your models here.



class ExpenseManager(models.Manager):

    def all(self, user=None, *args, **kwargs):
        return super(ExpenseManager, self).filter(user=user)

    def this_year(self, user=None, year=None, *args, **kwargs):
        if year:
            y = year
        else:
            y = get_ist_datetime().date().year
        qs = super(ExpenseManager, self).filter(user=user).filter(timestamp__year=y)
        return qs

    def this_month(self, user=None, year=None, month=None, *args, **kwargs):
        if month:
            m = month
        else:
            m = get_ist_datetime().date().month
        qs = Expense.objects.this_year(user=user, year=year).filter(timestamp__month=m)
        return qs

    def last_month(self, user=None, *args, **kwargs):
        today = get_ist_datetime().date()
        year = today.year
        last_month = (today.month - 1) or 12
        if last_month == 12:
            year -= 1
        qs = Expense.objects.this_year(user=user, year=year).filter(timestamp__month=last_month)
        return qs

    def this_day(self, user=None, year=None, month=None, day=None, *args, **kwargs):
        if day:
            d = day
        else:
            d = get_ist_datetime().date().day
        qs = Expense.objects.this_month(user=user, year=year, month=month).filter(timestamp__day=d)
        return qs

    def amount_sum(self, user=None, year=None, month=None, day=None, *args, **kwargs):
        total = {}
        qs = Expense.objects
        total['all'] = qs.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total['year'] = qs.this_year(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total['month'] = qs.this_month(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total['last_month'] = qs.last_month(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total['day'] = qs.this_day(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        return total


class Remark(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='remarks',
            on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name',)


class Expense(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='expenses',
            on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    remark = models.ForeignKey(Remark, null=True, blank=True, related_name='expenses',
                on_delete=models.SET_NULL)
    timestamp = models.DateField()

    objects = ExpenseManager()

    def __str__(self):
        return "{} : {} : {}".format(self.remark, self.amount, self.timestamp)

    class Meta():
        ordering = ("-timestamp", "-created_at",)


def preprocess_remark(instance, sender, *args, **kwargs):
    if instance.name:
        instance.name = instance.name.strip().lower()

pre_save.connect(preprocess_remark, sender=Remark)

