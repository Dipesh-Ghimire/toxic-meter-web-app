import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from facebook.models import FacebookComment, FacebookPost
from ml_integration.models import ToxicityParameters
from .services import get_user_posts
from users.models import UserProfile
from .models import CommentStats, DeletedComment
from ml_integration.services import store_bulk_predictions, store_single_prediction
from facebook.facebook_api import delete_facebook_comment, hide_facebook_comment , unhide_facebook_comment
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


# View for Analyzed Comments
@login_required
def analyzed_comments(request):
    """
    View analyzed comments with toxicity parameters, restricted to user-accessible posts.
    """
    user_posts = get_user_posts(request.user)
    comments = FacebookComment.objects.filter(
        toxicity_parameters__isnull=False,
        post__in=user_posts
    ).select_related('toxicity_parameters', 'post').order_by('-toxicity_parameters__predicted_at')

    search_query = request.GET.get('q')
    if search_query:
        comments = comments.filter(Q(content__icontains=search_query) | Q(user_name__icontains=search_query))
    for c in comments:
        c.post_id_display = c.post.post_id.split('_')[1]

    # Pagination (10 comments per page)
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'comments/analyzed_comments.html', {'page_obj': page_obj, 'comments': page_obj.object_list,'search_query': search_query})

# View for Unanalyzed Comments
@login_required
def unanalyzed_comments(request):
    """
    Fetch and display unanalyzed comments (no ToxicityParameters entry) restricted to user-accessible posts.
    """
    user_posts = get_user_posts(request.user)
    comments = FacebookComment.objects.filter(
        toxicity_parameters__isnull=True,
        post__in=user_posts
    ).select_related('post')
    search_query = request.GET.get('q')
    if search_query:
        comments = comments.filter(Q(content__icontains=search_query) | Q(user_name__icontains=search_query))
    # Pagination (10 comments per page)
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'comments/unanalyzed_comments.html', {'comments': page_obj,'search_query': search_query})

# Analyze Comment
@login_required
def analyze_comment(request, comment_id):
    """
    View to analyze a single comment and store toxicity predictions in the database.
    """
    success = store_single_prediction(comment_id)
    comment = FacebookComment.objects.get(id=comment_id)
    if success:
        try:
            stats = request.user.moderator_stats  # Assuming a relationship exists for the moderator
            stats.comments_analyzed += 1  # or len(comment_ids) for bulk actions
            stats.save()
        except CommentStats.DoesNotExist:
            CommentStats.objects.create(moderator=comment.post.moderator, comments_analyzed=1)
        messages.success(request, "Comment analyzed successfully.")
        # Redirect back to unanalyzed comments page after analysis
        return redirect('analyzed_comments')
    else:
        # Handle the error gracefully (optional)
        messages.error(request, "Failed to analyze the comment.")
        return redirect('unanalyzed_comments')
@login_required
def analyze_bulk_comments(request):
    """
    View to analyze all unanalyzed comments and store toxicity predictions in the database.
    """
    # Fetch IDs of unanalyzed comments
    comment_ids = FacebookComment.objects.filter(toxicity_parameters__isnull=True).values_list('id', flat=True)
    comment_count = len(list(comment_ids))
    # Perform bulk prediction and store results
    success = store_bulk_predictions(comment_ids)
    if success:
        try:
            stats = request.user.moderator_stats
            stats.comments_analyzed += comment_count
            stats.save()
        except CommentStats.DoesNotExist:
            CommentStats.objects.create(moderator=request.user, comments_analyzed=1)
        messages.success(request, f"{comment_count} comments analyzed successfully.")
        # Redirect back to unanalyzed comments page after analysis
        return redirect('unanalyzed_comments')
    else:
        # Handle the error gracefully (optional)
        messages.error(request, "Failed to analyze comments in bulk.")
        return redirect('analyzed_comments')
# Delete Comment
@login_required
def delete_comment(request, comment_id):
    """
    Deletes a specific comment from Facebook and the local database.

    Args:
        request: The HTTP request object.
        comment_id (str): The ID of the comment to be deleted.

    Returns:
        Redirects to the appropriate page with a success or error message.
    """
    # Ensure the user is a Moderator
    if request.user.userprofile.role != 'moderator':
        messages.error(request, "Only Moderators can delete comments.")
        return redirect('unanalyzed_comments')

    # Fetch the Moderator's assigned token
    user_profile = request.user.userprofile
    access_token = user_profile.facebook_access_token
    if not access_token:
        messages.error(request, "You do not have a valid Access Token.")
        return redirect('unanalyzed_comments')
    # Fetch the comment from the database
    comment = get_object_or_404(FacebookComment, id=comment_id)
    
    # Fetch toxicity parameters for the comment (if any)
    toxicity_parameters = ToxicityParameters.objects.filter(comment=comment).first()
    
    # Store the deleted comment with its toxicity parameters
    if toxicity_parameters:
        DeletedComment.objects.create(
            post=comment.post,  # Store the post directly
            comment_id=comment.comment_id,  # Store the comment_id directly
            content=comment.content,  # Store the content
            user_name=comment.user_name,
            toxic=toxicity_parameters.toxic,
            severe_toxic=toxicity_parameters.severe_toxic,
            obscene=toxicity_parameters.obscene,
            threat=toxicity_parameters.threat,
            insult=toxicity_parameters.insult,
            identity_hate=toxicity_parameters.identity_hate,
            reason_for_deletion=request.POST.get("reason_for_deletion", "Not specified")  # Optional reason
        )
    else:
        # If toxicity parameters are not available, still store the comment (without toxicity details)
        DeletedComment.objects.create(
            post=comment.post,  # Store the post directly
            comment_id=comment.comment_id,  # Store the comment_id directly
            content=comment.content,  # Store the content
            user_name=comment.user_name,
            reason_for_deletion=request.POST.get("reason_for_deletion", "Not specified")
        )

    # Call the function to delete the comment
    success = delete_facebook_comment(comment_id, access_token)
    if success:
        try:
            comment.delete()
            try:
                stats = request.user.moderator_stats
                stats.comments_deleted += 1
                stats.save()
            except CommentStats.DoesNotExist:
                CommentStats.objects.create(moderator=request.user, comments_deleted=1)
            messages.success(request, f"Comment with ID {comment_id} has been deleted from Facebook and the local database!")
        except FacebookComment.DoesNotExist:
            messages.warning(request, f"Comment with ID {comment_id} was deleted from Facebook but not found in the local database.")
    else:
        messages.error(request, f"Failed to delete comment with ID {comment_id}.")
    
    return redirect('analyzed_comments')

@login_required
def hide_comment(request, comment_id):
    """
    Hides a specific comment on Facebook.

    Args:
        request: The HTTP request object.
        comment_id (str): The ID of the comment to be hidden.

    Returns:
        Redirects to the appropriate page with a success or error message.
    """
    # Ensure the user is a Moderator
    if request.user.userprofile.role != 'moderator':
        messages.error(request, "Only Moderators can hide comments.")
        return redirect('unanalyzed_comments')

    # Fetch the Moderator's assigned token
    user_profile = request.user.userprofile
    access_token = user_profile.facebook_access_token
    if not access_token:
        messages.error(request, "You do not have a valid Access Token.")
        return redirect('unanalyzed_comments')

    # Call the function to hide the comment on Facebook
    success = hide_facebook_comment(comment_id, access_token)

    if success:
        messages.success(request, f"Comment with ID {comment_id} has been successfully hidden on Facebook!")
    else:
        messages.error(request, f"Failed to hide comment with ID {comment_id} on Facebook.")

    return redirect('analyzed_comments')

@login_required
def unhide_comment(request, comment_id):
    """
    Unhides a specific comment on Facebook.

    Args:
        request: The HTTP request object.
        comment_id (str): The ID of the comment to be unhidden.

    Returns:
        Redirects to the appropriate page with a success or error message.
    """
    # Ensure the user is a Moderator
    if request.user.userprofile.role != 'moderator':
        messages.error(request, "Only Moderators can unhide comments.")
        return redirect('unanalyzed_comments')

    # Fetch the Moderator's assigned token
    user_profile = request.user.userprofile
    access_token = user_profile.facebook_access_token
    if not access_token:
        messages.error(request, "You do not have a valid Access Token.")
        return redirect('unanalyzed_comments')

    # Call the function to unhide the comment on Facebook
    success = unhide_facebook_comment(comment_id, access_token)

    if success:
        try:
            stats = request.user.moderator_stats
            stats.comments_unhidden += 1
            stats.save()
        except CommentStats.DoesNotExist:
            CommentStats.objects.create(moderator=request.user, comments_unhidden=1)
        messages.success(request, f"Comment with ID {comment_id} has been successfully unhidden on Facebook!")
    else:
        messages.error(request, f"Failed to unhide comment with ID {comment_id} on Facebook.")

    return redirect('analyzed_comments')

@login_required
def deleted_comments(request):
    """
    View deleted comments.
    - Only accessible by Moderators.
    - Only shows deleted comments related to the Moderator's assigned admin.
    """
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.assigned_by:
        admin_profile = UserProfile.objects.get(user=user_profile.assigned_by)
        
        # Get posts fetched by the assigned admin
        user_posts = FacebookPost.objects.filter(fetched_by=admin_profile.user)

        # Fetch only deleted comments that match the user's posts
        deleted_comments = DeletedComment.objects.filter(post__in=user_posts).order_by('-deleted_at')
    elif user_profile.role == 'admin':
        user_posts = FacebookPost.objects.filter(fetched_by=request.user)
        deleted_comments = DeletedComment.objects.filter(post__in=user_posts).order_by('-deleted_at')
    else:
        deleted_comments = DeletedComment.objects.none()  # No assigned admin, no deleted comments
    search_query = request.GET.get('q')
    if search_query:
        deleted_comments = deleted_comments.filter(Q(content__icontains=search_query) | Q(user_name__icontains=search_query))
    for c in deleted_comments:
        c.comment_id_display = c.comment_id.split('_')[1] if '_' in c.comment_id else c.comment_id

    # Handle CSV Download
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="deleted_comments.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Comment ID', 'Content', 'Toxic', 'Severe Toxic', 'Obscene', 'Threat', 'Insult', 'Identity Hate', 'Reason for Deletion', 'Deleted At'
        ])

        for comment in deleted_comments:
            writer.writerow([
                comment.comment_id,
                comment.content,
                1 if comment.toxic else 0,
                1 if comment.severe_toxic else 0,
                1 if comment.obscene else 0,
                1 if comment.threat else 0,
                1 if comment.insult else 0,
                1 if comment.identity_hate else 0,
                comment.reason_for_deletion,
                comment.deleted_at
            ])

        return response

    return render(request, 'comments/deleted_comments.html', {
        'deleted_comments': deleted_comments,
        'search_query': search_query
    })

@login_required
def edit_toxicity_labels(request, comment_id):
    """
    Allows moderators to manually edit toxicity labels of a comment via a modal form.
    """
    comment = get_object_or_404(FacebookComment, id=comment_id)

    if request.method == "POST":
        toxicity_params = comment.toxicity_parameters

        # Update toxicity labels based on form submission
        toxicity_params.toxic = 'toxic' in request.POST
        toxicity_params.severe_toxic = 'severe_toxic' in request.POST
        toxicity_params.obscene = 'obscene' in request.POST
        toxicity_params.threat = 'threat' in request.POST
        toxicity_params.insult = 'insult' in request.POST
        toxicity_params.identity_hate = 'identity_hate' in request.POST

        # Save updated parameters
        toxicity_params.save()
        stats = request.user.moderator_stats
        stats.comments_manually_tagged += 1
        stats.save()
        messages.success(request, f"Manually Tagged Toxicity labels for comment {comment_id}")

    return redirect('analyzed_comments')

def paginate_comments(request, comments_list):
    """
    Helper function to paginate the comments queryset.
    """
    paginator = Paginator(comments_list, 10)  # Show 10 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj