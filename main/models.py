import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.response import Response

def generate_unique_code():
    return str(uuid.uuid4())[:30]

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    def __str__(self):
        return self.username

class UserReletion(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to')
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    def __str__(self):
        return f"{self.from_user.username} - {self.to_user.username}"

class Chat(models.Model):
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    @property
    def last_message(self):
        message = Message.objects.filter(chat = self).last()
        return message
    
    @property
    def unread_messages(self):
        quantity = Message.objects.filter(
            chat = self,
            is_read = False
            ).count()
        return quantity
    


class ChatUser(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    def save(self, *args, **kwargs):
        if ChatUser.objects.filter(chat=self.chat).count() >= 2:
            raise ValueError('A chat can have at most 2 users.')
        super().save(*args, **kwargs)

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    body = models.TextField()
    file = models.FileField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    def __str__(self):
        return f"{self.chat.id}-> {self.author.id}"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    def files(self):
        return self.postfiles_set.all()

class PostFiles(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.FileField(upload_to='post/')
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

    def delete(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, str(self.file))
        if os.path.isfile(file_path):
            os.remove(file_path)
        super().delete(*args, **kwargs)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    reply = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)

class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    status = models.BooleanField()  # True = like , False = dislike
    code = models.CharField(max_length=30, unique=True, default=generate_unique_code)
