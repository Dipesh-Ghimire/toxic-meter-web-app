from django.urls import path
from . import views

urlpatterns = [
    path('analyzed/', views.analyzed_comments, name='analyzed_comments'),
    path('unanalyzed/', views.unanalyzed_comments, name='unanalyzed_comments'),
    path('deleted/', views.deleted_comments, name='deleted_comments'),
    #path('update_comment_tags/<int:comment_id>/', views.update_comment_tags, name='update_comment_tags'),
    path('analyze/<int:comment_id>/', views.analyze_comment, name='analyze_comment'),
    path('delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('hide/<int:comment_id>/', views.hide_comment, name='hide_comment'),
    path('unhide/<int:comment_id>/', views.unhide_comment, name='unhide_comment'),
    path('analyze/bulk/', views.analyze_bulk_comments, name='analyze_bulk_comments'),
    path('edit_toxicity_labels/<int:comment_id>/', views.edit_toxicity_labels, name='edit_toxicity_labels'),

]