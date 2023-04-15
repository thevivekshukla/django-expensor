from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.utils import timezone

from utils.base_model import BaseModel
from utils.helpers import get_ist_datetime

# Create your models here.


class ExpenseManager(models.Manager):
    def all(self, user=None, *args, **kwargs):
        return super(ExpenseManager, self).filter(user=user)

    def this_year(self, user=None, year=None, *args, **kwargs):
        year = year if year else get_ist_datetime().year
        qs = super(ExpenseManager, self).filter(user=user).filter(timestamp__year=year)
        return qs

    def this_month(self, user=None, year=None, month=None, *args, **kwargs):
        month = month if month else get_ist_datetime().month
        qs = Expense.objects.this_year(user=user, year=year).filter(
            timestamp__month=month
        )
        return qs

    def last_month(self, user=None, *args, **kwargs):
        today = get_ist_datetime().date()
        first_day = today.replace(day=1)
        prev_month = first_day - timedelta(days=7)
        qs = Expense.objects.this_month(
            user=user, year=prev_month.year, month=prev_month.month
        )
        return qs

    def this_day(self, user=None, year=None, month=None, day=None, *args, **kwargs):
        day = day if day else get_ist_datetime().day
        qs = Expense.objects.this_month(user=user, year=year, month=month).filter(
            timestamp__day=day
        )
        return qs

    def amount_sum(self, user=None, year=None, month=None, day=None, *args, **kwargs):
        total = {}
        qs = Expense.objects
        total["all"] = qs.filter(user=user).aggregate(Sum("amount"))["amount__sum"] or 0
        total["year"] = (
            qs.this_year(user=user).aggregate(Sum("amount"))["amount__sum"] or 0
        )
        total["month"] = (
            qs.this_month(user=user).aggregate(Sum("amount"))["amount__sum"] or 0
        )
        total["last_month"] = (
            qs.last_month(user=user).aggregate(Sum("amount"))["amount__sum"] or 0
        )
        total["day"] = (
            qs.this_day(user=user).aggregate(Sum("amount"))["amount__sum"] or 0
        )

        return total


class Remark(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="remarks", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (
            "user",
            "name",
        )
        indexes = [models.Index(fields=("user", "name"))]


class Expense(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="expenses", on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField()
    remark = models.ForeignKey(
        Remark,
        null=True,
        blank=True,
        related_name="expenses",
        on_delete=models.SET_NULL,
    )
    timestamp = models.DateField()

    objects = ExpenseManager()

    def __str__(self):
        return "{} : {} : {}".format(self.remark, self.amount, self.timestamp)

    class Meta:
        indexes = [
            models.Index(
                fields=(
                    "user",
                    "-timestamp",
                    "-created_at",
                )
            ),
        ]
        ordering = (
            "-timestamp",
            "-created_at",
        )


def preprocess_remark(instance, sender, *args, **kwargs):
    if instance.name:
        instance.name = instance.name.strip().lower()


pre_save.connect(preprocess_remark, sender=Remark)
