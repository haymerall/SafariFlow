from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model for SafariFlow.
    We use a custom model from the beginning to allow future customization.
    """
    pass
