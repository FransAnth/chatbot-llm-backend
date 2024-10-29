from django.db import models


class ChatConversation(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.TextField(max_length=200)
    question = models.TextField(default="")
    answer = models.TextField(default="")
    timestamp = models.DateTimeField(auto_now_add=True)
