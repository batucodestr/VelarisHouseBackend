from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        blank=False
    )
    