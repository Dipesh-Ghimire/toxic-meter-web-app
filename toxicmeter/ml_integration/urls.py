from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_toxicity_single, name='predict_toxicity_single'),
    path('bulk/', views.predict_toxicity_bulk, name='predict_toxicity_bulk'),
]