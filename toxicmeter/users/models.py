from django.db import models
from django.contrib.auth.models import User

# Role choices for users
USER_ROLES = [
    ('admin', 'Admin'),
    ('moderator', 'Moderator'),
]

# UserProfile model to extend User with roles
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='moderator')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
