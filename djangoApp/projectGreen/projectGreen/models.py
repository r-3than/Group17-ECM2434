from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    '''
    Notifications model
    '''
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)