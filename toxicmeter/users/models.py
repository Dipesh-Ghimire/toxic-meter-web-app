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
    facebook_access_token = models.CharField(max_length=500, blank=True, null=True)  # Token
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True)  # Page ID
    token_active = models.BooleanField(default=False)  # Whether token is active
    assigned_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tokens")

    def __str__(self):
        return f"{self.user.username} ({self.role})"
