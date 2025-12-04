from django.db import models
from django.conf import settings


class Message(models.Model):
    # Use the AUTH_USER_MODEL string to avoid resolving the user model at import time
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.content[:20]}"
