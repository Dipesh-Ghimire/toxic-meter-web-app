from django.urls import path
from . import views

urlpatterns = [
    path('fetch-posts/', views.fetch_posts, name='fetch_posts'),
    path('posts/', views.view_posts, name='view_posts'),  # View all posts
    path('fetch-comments/<str:post_id>/', views.fetch_comments, name='fetch_comments'),  # Fetch comments for a post
]
