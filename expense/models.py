from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.conf import settings
from django.db.models.signals import pre_save

from datetime import date

from utils.base_model import BaseModel

# Create your models here.



class ExpenseManager(models.Manager):
    def all(self, user=None, *args, **kwargs):
        return super(ExpenseManager, self).filter(user=user)

    def this_year(self, user=None, year=None, *args, **kwargs):
        if year:
            y = year
        else:
            y = date.today().year
        qs = super(ExpenseManager, self).filter(user=user).filter(timestamp__year=y)
        return qs

    def this_month(self, user=None, year=None, month=None, *args, **kwargs):
        if month:
            m = month
        else:
            m = date.today().month
        qs = Expense.objects.this_year(user=user, year=year).filter(timestamp__month=m)
        return qs

    def last_month(self, user=None, *args, **kwargs):
        qs = Expense.objects.this_year(user=user).filter(timestamp__month=date.today().month-1)
        return qs

    def this_day(self, user=None, year=None, month=None, day=None, *args, **kwargs):
        if day:
            d = day
        else:
            d = date.today().day
        qs = Expense.objects.this_month(user=user, year=year, month=month).filter(timestamp__day=d)
        return qs


    def amount_sum(self, user=None, year=None, month=None, day=None, *args, **kwargs):
        total = {}
        qs = Expense.objects
        total['all'] = qs.filter(user=user).aggregate(Sum('amount'))['amount__sum']
        total['year'] = qs.this_year(user=user).aggregate(Sum('amount'))['amount__sum']
        total['month'] = qs.this_month(user=user).aggregate(Sum('amount'))['amount__sum']
        total['last_month'] = qs.last_month(user=user).aggregate(Sum('amount'))['amount__sum']
        total['day'] = qs.this_day(user=user).aggregate(Sum('amount'))['amount__sum']

        return total



class Remark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Expense(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.PositiveIntegerField()
    remark = models.ForeignKey(Remark, null=True, blank=True)
    timestamp = models.DateField()

    objects = ExpenseManager()

    def __str__(self):
        return "{} : {} : {}".format(self.remark, self.amount, self.timestamp)

    class Meta():
        ordering = ["-timestamp"]


def capitalize_remark(instance, sender, *args, **kwargs):
    if instance.name:
        instance.name = instance.name.title()

pre_save.connect(capitalize_remark, sender=Remark)
