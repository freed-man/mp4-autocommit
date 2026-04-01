from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    User profile for maintaining default contact info
    and order history.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    default_phone_number = models.CharField(
        max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"