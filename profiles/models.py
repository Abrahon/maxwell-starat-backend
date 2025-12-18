from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )

    full_name = models.CharField(max_length=150)
    institution_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)

    profile_photo = CloudinaryField(
        "profile_photo",
        blank=True,
        null=True
    )
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user})"
