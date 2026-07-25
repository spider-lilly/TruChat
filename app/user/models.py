# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"


    # Email login
    email = models.EmailField(unique=True)

    # This is intentionally separate from Django's is_active flag.
    is_verified = models.BooleanField(default=False)

    # User role
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    # Login field
    USERNAME_FIELD = "email"

    # Required while creating superuser
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
