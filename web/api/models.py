from django.db import models


class Task(models.Model):

    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    url = models.CharField(max_length=256)
    path = models.CharField(max_length=256)
    status = models.CharField(choices=STATUSES, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(default="None")
