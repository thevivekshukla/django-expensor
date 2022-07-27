from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.fields import related

from utils.base_model import BaseModel

User = get_user_model()

# Create your models here.


class Source(BaseModel):
    user = models.ForeignKey(User, related_name='sources', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name',)


class Income(BaseModel):
    user = models.ForeignKey(User, related_name='incomes', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    source = models.ForeignKey(Source, blank=True, null=True, related_name='incomes',
                on_delete=models.SET_NULL)
    timestamp = models.DateField()

    def __str__(self):
        return "{} : {}".format(self.user, self.source)

    class Meta():
        ordering = ('-timestamp', '-created_at',)


class SavingCalculation(BaseModel):
    user = models.OneToOneField(User, related_name='saving_calculation', on_delete=models.CASCADE)
    savings_fixed_amount = models.PositiveIntegerField(help_text='fixed amount that must be saved if possible. 0 to ignore')
    auto_fill_savings_fixed_amount = models.BooleanField(default=False, blank=True)
    savings_percentage = models.PositiveIntegerField(help_text='in percentage') # of the total amount
    amount_to_keep_in_bank = models.PositiveIntegerField(help_text='Should be less than monthly salary. i.e. <=90% of monthly salary')
    auto_fill_amount_to_keep_in_bank = models.BooleanField(default=False, blank=True)
    message = models.TextField(null=True, blank=True, help_text="briefly explain your thought process on choosing this method")
    amount_in_multiples_of = models.PositiveIntegerField(default=100, blank=False, null=False, help_text='i.e. 100, 1000, etc')

    def __str__(self):
        return f'{self.user}'


class InvestmentEntity(BaseModel):
    saving_calculation = models.ForeignKey(SavingCalculation, related_name='investment_entity',
                            on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    percentage = models.PositiveIntegerField(help_text='in percentage', blank=True, default=0)

    def __str__(self):
        return f'{self.saving_calculation}: {self.name}'

    class Meta:
        ordering = ('created_at',)
        unique_together = ('saving_calculation', 'name',)


