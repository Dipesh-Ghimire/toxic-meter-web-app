from facebook.models import FacebookPost
from users.models import UserProfile


def get_user_posts(user):
    """
    Returns the queryset of FacebookPost objects that the user has access to:
    - Admins: Only their own fetched posts.
    - Moderators: Only posts fetched by their assigned admin.
    """
    user_profile = UserProfile.objects.get(user=user)

    if user_profile.role == 'admin':
        # Admin sees only their own fetched posts
        return FacebookPost.objects.filter(fetched_by=user)

    elif user_profile.role == 'moderator' and user_profile.assigned_by:
        # Moderator sees only posts fetched by their assigned admin
        return FacebookPost.objects.filter(fetched_by=user_profile.assigned_by)

    return FacebookPost.objects.none()  # Default: No posts