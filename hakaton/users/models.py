from django.contrib.auth.models import User
from django.db import models

class Topic(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    tone = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')

class Question(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    text = models.TextField()
    answer = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')