import requests
from .models import FacebookPost
from datetime import datetime

def fetch_facebook_posts(page_id, access_token):
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

        # Iterate through the posts returned by the API
        for post in data.get('data', []):
            if post['id'] not in existing_post_ids:  # Check if post is already in the database
                FacebookPost.objects.create(
                    post_id=post['id'],
                    message=post.get('message', ''),
                    created_at=datetime.strptime(post['created_time'], "%Y-%m-%dT%H:%M:%S%z"),
                )
        return True
    else:
        print(f"Failed to fetch posts: {response.status_code} - {response.text}")
        return False
