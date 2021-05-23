from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.fields import related

from utils.base_model import BaseModel

User = get_user_model()

# Create your models here.


class Source(BaseModel):
    user = models.ForeignKey(User, related_name='sources', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    

class Income(BaseModel):
    user = models.ForeignKey(User, related_name='incomes', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    source = models.ForeignKey(Source, blank=True, null=True, related_name='incomes',
                on_delete=models.SET_NULL)
    timestamp = models.DateField()

    def __str__(self):
        return "{} : {}".format(self.user, self.source)

    class Meta():
        ordering = ('-timestamp', )