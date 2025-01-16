from django.shortcuts import redirect,render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FacebookPost
from .facebook_api import fetch_facebook_posts,fetch_facebook_comments

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
    # Ensure the user is a Moderator
    if request.user.userprofile.role != 'moderator':
        messages.error(request, "Only Moderators can view posts.")
        return redirect('dashboard')

    # Retrieve all Facebook posts from the database
    posts = FacebookPost.objects.all().order_by('-created_at')  # Display newest posts first
    # Slicing post_id to only show the second part
    for post in posts:
        post.post_id_display = post.post_id.split('_')[1]
    return render(request, 'facebook/posts.html', {'posts': posts})

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
