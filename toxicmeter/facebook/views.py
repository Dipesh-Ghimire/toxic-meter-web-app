from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .facebook_api import fetch_facebook_posts

@login_required
def fetch_posts(request):
    # Ensure the user is a moderator
    user_profile = request.user.userprofile
    if user_profile.role != 'moderator':
        messages.error(request, "Only Moderators can fetch posts.")
        return redirect('dashboard')

    # Check if the moderator has an assigned Access Token and Page ID
    access_token = user_profile.facebook_access_token
    page_id = user_profile.facebook_page_id
    if not access_token or not page_id:
        messages.error(request, "You do not have a valid Access Token or Page ID assigned.")
        return redirect('dashboard')

    # Fetch posts using the assigned token and page ID
    success = fetch_facebook_posts(page_id, access_token)
    if success:
        messages.success(request, "Posts fetched and stored successfully!")
    else:
        messages.error(request, "Failed to fetch posts. Please check your Access Token and Page ID.")
    
    return redirect('dashboard')

