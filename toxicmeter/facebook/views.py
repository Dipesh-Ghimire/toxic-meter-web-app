from django.shortcuts import redirect,render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import UserProfile
from .models import FacebookPost
from .facebook_api import fetch_facebook_posts,fetch_facebook_comments
from django.db.models import Q

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
    success = fetch_facebook_posts(page_id, access_token, request)
    if success:
        messages.success(request, "Posts fetched and stored successfully!")
    else:
        messages.error(request, "Failed to fetch posts. Please check your Access Token and Page ID.")
    
    return redirect('view_posts')

@login_required
def view_posts(request):
    """
    Ensure only the corresponding admin and their assigned moderators can view posts.
    """
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.role == 'admin':
        # Admin can only see posts they fetched
        posts = FacebookPost.objects.filter(fetched_by=request.user).order_by('-created_at')

    elif user_profile.role == 'moderator' and user_profile.assigned_by:
        # Moderator can only see posts fetched by their assigned admin
        posts = FacebookPost.objects.filter(fetched_by=user_profile.assigned_by).order_by('-created_at')

    else:
        # Default: No access
        messages.error(request, "You are not authorized to view these posts.")
        return redirect('dashboard')
    # Handle Search Query
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(Q(post_id__icontains=search_query) | Q(message__icontains=search_query))
    # Modify post_id display format
    for post in posts:
        post.post_id_display = post.post_id.split('_')[1]

    return render(request, 'facebook/posts.html', {'posts': posts,'search_query': search_query})

@login_required
def fetch_comments(request, post_id):
    post_id = str(post_id)  # Explicitly cast to string
    # Ensure the user is a Moderator
    if request.user.userprofile.role != 'moderator':
        messages.error(request, "Only Moderators can fetch comments.")
        return redirect('view_posts')

    # Fetch the Moderator's assigned token and page ID
    user_profile = request.user.userprofile
    access_token = user_profile.facebook_access_token
    if not access_token:
        messages.error(request, "You do not have a valid Access Token.")
        return redirect('view_posts')

    # Fetch comments for the given post using the token
    success = fetch_facebook_comments(post_id, access_token,request)
    if success:
        messages.success(request, f"Comments for post {post_id} have been fetched successfully!")
    else:
        messages.error(request, f"Failed to fetch comments for post {post_id}.")
    
    return redirect('view_posts')
