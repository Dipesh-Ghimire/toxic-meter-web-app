from django.db import models
from django.contrib.auth.models import User
# Model to store Facebook posts
class FacebookPost(models.Model):
    post_id = models.CharField(max_length=255, unique=True)  # Facebook Post ID
    message = models.CharField(max_length=500, blank=True, null=True)  # Post content or title
    created_at = models.DateTimeField()  # Original creation time on Facebook
    fetched_at = models.DateTimeField(auto_now_add=True)  # When fetched
    fetched_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fetched_posts',null=True,blank=True)  # User who fetched the post
    def __str__(self):
        return f"Post ID: {self.post_id} - {self.message[:30]}"

# Model to store Facebook comments
class FacebookComment(models.Model):
    post = models.ForeignKey(FacebookPost, on_delete=models.CASCADE, related_name='comments')
    comment_id = models.CharField(max_length=255, unique=True)  # Comment ID
    user_name = models.CharField(max_length=255)  # Name of the commenter
    content = models.TextField()  # The comment text
    created_at = models.DateTimeField()  # Original creation time
    fetched_at = models.DateTimeField(auto_now_add=True)  # When fetched
    is_hidden = models.BooleanField(default=False)  # Whether the comment is hidden by the user
    def __str__(self):
        return f"Comment by {self.user_name} on Post {self.post.post_id}"
