from django.urls import path
from . import views

urlpatterns = [
    path('fetch-posts/', views.fetch_posts, name='fetch_posts'),
]
