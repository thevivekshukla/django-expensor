from django.db import models
from django.contrib.auth import get_user_model

from utils.base_model import BaseModel

User = get_user_model()

# Create your models here.


class Source(BaseModel):

    user = models.ForeignKey(User,models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    

class Income(BaseModel):

    user = models.ForeignKey(User, models.CASCADE)
    amount = models.PositiveIntegerField()
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.DO_NOTHING)
    timestamp = models.DateField()

    def __str__(self):
        return "{} : {}".format(self.user, self.source)

    class Meta():
        ordering = ('-timestamp', )