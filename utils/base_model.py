from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    last_modified_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        abstract = True
