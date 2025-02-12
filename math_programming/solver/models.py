from django.db import models

class Problem(models.Model):
    parameters = models.JSONField()
    constraints = models.JSONField()
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)