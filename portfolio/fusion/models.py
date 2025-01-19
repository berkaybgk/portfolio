from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link the chat to a user
    message = models.TextField()  # User's message
    response = models.TextField()  # AI's response
    timestamp = models.DateTimeField(auto_now_add=True)  # When the message was created

