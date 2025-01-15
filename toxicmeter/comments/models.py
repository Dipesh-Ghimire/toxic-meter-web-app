from django.db import models

# Create your models here.
class DeletedComment(models.Model):
    comment_id = models.CharField(max_length=255, unique=True)  # Store comment_id directly
    content = models.TextField()  # The content of the deleted comment
    user_name = models.CharField(max_length=255, blank=True, null=True)  # The name of the user who posted the comment
    toxic = models.BooleanField(default=False)
    severe_toxic = models.BooleanField(default=False)
    obscene = models.BooleanField(default=False)
    threat = models.BooleanField(default=False)
    insult = models.BooleanField(default=False)
    identity_hate = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now_add=True)  # Date and time when the comment was deleted
    reason_for_deletion = models.TextField(blank=True, null=True)  # Reason for deletion (optional)

    def __str__(self):
        return f"Deleted Comment ID: {self.comment_id} - Toxicity: {self.toxic}"