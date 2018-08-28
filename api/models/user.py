from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    added_field = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.username}'