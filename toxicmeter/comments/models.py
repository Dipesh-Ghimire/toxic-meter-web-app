from django.db import models
from django.contrib.auth.models import User
from facebook.models import FacebookPost
# Create your models here.
class DeletedComment(models.Model):
    post = models.ForeignKey(FacebookPost, on_delete=models.CASCADE, related_name='deleted_comments', null=True, blank=True)
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

class CommentStats(models.Model):
    moderator = models.OneToOneField(User, on_delete=models.CASCADE, related_name="moderator_stats")

    # Comments-related counters
    comments_analyzed = models.PositiveIntegerField(default=0)  # Total comments analyzed
    comments_fetched = models.PositiveIntegerField(default=0)   # Total comments fetched from Facebook
    comments_deleted = models.PositiveIntegerField(default=0)   # Total comments deleted
    comments_hidden = models.PositiveIntegerField(default=0)    # Total comments hidden
    comments_unhidden = models.PositiveIntegerField(default=0)  # Total comments unhidden
    comments_manually_tagged = models.PositiveIntegerField(default=0)  # Total comments manually tagged
    is_model_serving = models.BooleanField(default=False)  # Is the model serving comments?
    # Posts-related counters
    posts_fetched = models.PositiveIntegerField(default=0)      # Total posts fetched from Facebook

    # Time tracking
    last_updated = models.DateTimeField(auto_now=True)  # Automatically track the last update

    def __str__(self):
        return f"Moderator Stats for {self.moderator.username}"