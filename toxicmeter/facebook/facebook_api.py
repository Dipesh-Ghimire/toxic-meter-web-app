import requests
from comments.models import CommentStats
from users.models import UserProfile
from .models import FacebookPost, FacebookComment
from datetime import datetime
from django.utils.dateparse import parse_datetime

def fetch_facebook_posts(page_id, access_token, request):
    """
    Fetch posts from a Facebook Page using Graph API.
    Fetches only new posts that are not already in the database.
    """
    base_url = f"https://graph.facebook.com/v21.0/{page_id}/posts"
    headers = {
        'Authorization': f'Bearer {access_token}',  # Bearer token for authentication
    }
    params = {
        'fields': 'id,message,created_time',  # Specify fields to fetch
        'limit': 100,  # Optional: Adjust to control how many posts are fetched per request
    }

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()

        # Get all post IDs currently in the database for this page
        existing_post_ids = set(FacebookPost.objects.values_list('post_id', flat=True))
        counter = 0
        user_profile = UserProfile.objects.get(user=request.user)
        # If user is a moderator, assign post to their admin instead
        if user_profile.role == 'moderator' and user_profile.assigned_by:
            fetched_by = user_profile.assigned_by  # Assign the admin
        else:
            fetched_by = request.user
        # Iterate through the posts returned by the API
        for post in data.get('data', []):
            if post['id'] not in existing_post_ids:  # Check if post is already in the database
                counter += 1
                FacebookPost.objects.create(
                    post_id=post['id'],
                    message=post.get('message', ''),
                    created_at=datetime.strptime(post['created_time'], "%Y-%m-%dT%H:%M:%S%z"),
                    fetched_by=fetched_by
                )
        try:
            stats = request.user.moderator_stats  # Assuming moderator_stats exists for the moderator
            stats.posts_fetched += counter
            stats.save()
        except CommentStats.DoesNotExist:
            CommentStats.objects.create(moderator=request.user, posts_fetched=counter)
        return True
    else:
        print(f"Failed to fetch posts: {response.status_code} - {response.text}")
        return False

def fetch_facebook_comments(post_id, access_token, request):
    # API call to fetch comments for the given post
    url = f"https://graph.facebook.com/v21.0/{post_id}/comments"
    params = {
        'access_token': access_token,
    }
    response = requests.get(url, params=params)
    data = response.json()
    moderator = request.user
    # Error handling for API response
    if 'error' in data:
        print(f"Error fetching comments: {data['error']['message']}")
        return False
    new_comments_count = 0
    # Iterate over and save comments
    for comment in data.get('data', []):
        comment_id = str(comment['id'])  # Ensure it's treated as a string
        content = comment.get('message', '')
        user_name = comment.get('from', {}).get('name', 'Unknown')
        created_at = parse_datetime(comment['created_time'])

        # Ensure post ID is treated as a string
        try:
            post = FacebookPost.objects.get(post_id=str(post_id))
            # Ensure no duplicate comments are saved
            comment_obj, created = FacebookComment.objects.get_or_create(
                comment_id=comment_id,
                defaults={
                    'post': post,
                    'user_name': user_name,
                    'content': content,
                    'created_at': created_at,
                },
            )
            if created:
                new_comments_count += 1
        except FacebookPost.DoesNotExist:
            print(f"Post with ID {post_id} does not exist in the database.")
    try:
        stats = moderator.moderator_stats  # Assuming moderator_stats exists for the moderator
        stats.comments_fetched += new_comments_count
        stats.save()
    except CommentStats.DoesNotExist:
        CommentStats.objects.create(moderator=moderator, comments_fetched=new_comments_count)
    return True

def delete_facebook_comment(comment_id, access_token):
    """
    Deletes a comment both from Facebook and the local database.

    Args:
        comment_id (str): The DB comment ID.
        access_token (str): The access token for making Facebook API requests.

    Returns:
        bool: True if the comment was successfully deleted, False otherwise.
    """
    import requests
    from facebook.models import FacebookComment

    # Delete the comment from Facebook
    fb_cmt_id = FacebookComment.objects.get(id=comment_id).comment_id
    url = f"https://graph.facebook.com/v21.0/{fb_cmt_id}"
    params = {
        'access_token': access_token,
    }
    response = requests.delete(url, params=params)
    
    if response.status_code == 200:
        # Successfully deleted from Facebook, now delete from the database
        try:
            FacebookComment.objects.get(id=comment_id).delete()
            return True
        except FacebookComment.DoesNotExist:
            print(f"Comment with ID {comment_id} does not exist in the database.")
            return False
    else:
        print(f"Error deleting comment from Facebook: {response.json().get('error', {}).get('message', 'Unknown error')}")
        return False

def hide_facebook_comment(comment_id, access_token):
    try:
        fb_cmt_id = FacebookComment.objects.get(id=comment_id).comment_id
    except FacebookComment.DoesNotExist:
        print(f"FacebookComment with ID {comment_id} does not exist.")
        return False
    url = f"https://graph.facebook.com/v21.0/{fb_cmt_id}"
    params = {
        'is_hidden': 'TRUE',
        'access_token': access_token,
    }
    try:
        response = requests.post(url, data=params)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('success'):
            FacebookComment.objects.filter(id=comment_id).update(is_hidden=True)
            return True
        else:
            print(f"Error hiding comment: {response_data}")
            return False
    except requests.RequestException as e:
        print(f"Error while hiding comment: {e}")
        return False
    
def unhide_facebook_comment(comment_id, access_token):
    """
    Unhides a specific comment on Facebook.

    Args:
        comment_id (str): The ID of the comment according to database to unhide.
        access_token (str): The access token of the moderator.

    Returns:
        bool: True if the comment was successfully unhidden, False otherwise.
    """
    fb_cmt_id = FacebookComment.objects.get(id=comment_id).comment_id
    url = f"https://graph.facebook.com/v21.0/{fb_cmt_id}"
    params = {
        'is_hidden': 'FALSE',
        'access_token': access_token,
    }
    try:
        response = requests.post(url, data=params)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('success'):
            FacebookComment.objects.filter(id=comment_id).update(is_hidden=False)
            return True
        else:
            print(f"Error unhiding comment: {response_data}")
            return False
    except requests.RequestException as e:
        print(f"Error while unhiding comment: {e}")
        return False
