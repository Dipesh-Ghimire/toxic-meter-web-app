from django.contrib import admin
from facebook.models import FacebookPost, FacebookComment
from ml_integration.models import ToxicityParameters
from comments.models import CommentStats, DeletedComment
from .models import UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(FacebookPost)
admin.site.register(FacebookComment)
admin.site.register(ToxicityParameters)
admin.site.register(DeletedComment)
admin.site.register(CommentStats)