from django.urls import path
from ml_integration.views import predict_toxicity_single, predict_toxicity_bulk
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-token/', views.manage_access_token, name='manage_token'),
    path('predict_single/<int:comment_id>/',predict_toxicity_single, name='predict_single'),
    path('predict_bulk/', predict_toxicity_bulk, name='predict_bulk'),
    path('remove-moderator/<int:moderator_id>/', views.remove_moderator, name='remove_moderator'),
]
