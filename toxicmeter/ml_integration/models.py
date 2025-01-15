from django.db import models
from facebook.models import FacebookComment

class ToxicityParameters(models.Model):
    comment = models.OneToOneField(FacebookComment, on_delete=models.CASCADE, related_name='toxicity_parameters')
    toxic = models.BooleanField(default=False)
    severe_toxic = models.BooleanField(default=False)
    obscene = models.BooleanField(default=False)
    threat = models.BooleanField(default=False)
    insult = models.BooleanField(default=False)
    identity_hate = models.BooleanField(default=False)
    predicted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Toxicity Parameters for Comment ID: {self.comment.id}"
