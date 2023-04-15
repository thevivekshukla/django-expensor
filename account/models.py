from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete, post_save

from utils.base_model import BaseModel
from utils.helpers import get_ist_datetime

User = get_user_model()

# Create your models here.


class AccountName(BaseModel):
    TYPES = [
        (0, "Liability"),
        (1, "Asset"),
    ]
    user = models.ForeignKey(
        User, related_name="account_names", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)
    type = models.IntegerField(choices=TYPES)

    def __str__(self):
        return f"{self.user} - {self.name}"

    class Meta:
        ordering = (
            "name",
            "created_at",
        )
        unique_together = (
            "user",
            "name",
            "type",
        )
        indexes = [
            models.Index(fields=["user", "name"]),
        ]


class AccountNameAmount(BaseModel):
    account_name = models.ForeignKey(
        AccountName, related_name="amounts", on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.account_name}: {self.amount}"

    class Meta:
        ordering = (
            "-date",
            "-created_at",
        )
        unique_together = (
            "account_name",
            "date",
        )
        indexes = [
            models.Index(
                fields=(
                    "account_name",
                    "-date",
                )
            ),
        ]


def _save_networth(instance, *args, **kwargs):
    today_date = get_ist_datetime().date()
    user = instance.account_name.user
    account_names = user.account_names.all()
    networth_amount = 0
    for account in account_names:
        account_amount = account.amounts.order_by("-date").first()
        if account_amount:
            if account.type == 0:
                networth_amount -= account_amount.amount
            else:
                networth_amount += account_amount.amount
    try:
        networth = NetWorth.objects.get(user=user, date=today_date)
        networth.amount = networth_amount
        networth.save()
    except NetWorth.DoesNotExist:
        NetWorth.objects.create(user=user, amount=networth_amount, date=today_date)


post_save.connect(_save_networth, sender=AccountNameAmount)
post_delete.connect(_save_networth, sender=AccountNameAmount)


class NetWorth(BaseModel):
    user = models.ForeignKey(User, related_name="net_worth", on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.user} - {self.amount}"

    class Meta:
        ordering = (
            "-date",
            "-created_at",
        )
        unique_together = (
            "user",
            "date",
        )
        indexes = [
            models.Index(
                fields=[
                    "user",
                    "-date",
                ]
            ),
        ]
