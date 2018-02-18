from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class Source(models.Model):

    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    

class Income(models.Model):

    user = models.ForeignKey(User)
    amount = models.PositiveIntegerField()
    source = models.ForeignKey(Source, blank=True, null=True)
    timestamp = models.DateField()

    def __str__(self):
        return "{} : {}".format(self.user, self.source)

    class Meta():
        ordering = ('-timestamp', )