from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from facebook.models import FacebookComment, FacebookPost
from ml_integration.services import store_single_prediction
from ml_integration.models import ToxicityParameters

from .models import UserProfile
from .forms import AssignTokenForm, UserRegisterForm, UserLoginForm, AdminTokenForm
from django.contrib import messages
from comments.models import CommentStats, DeletedComment

# Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Login View
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

# Logout View
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# Dashboard View (accessible after login)
@login_required
def dashboard(request):
    # Check if the logged-in user is an admin
    def checkModelServing():
        comment = FacebookComment.objects.first()
        print(comment)
        if comment:
            success = store_single_prediction(comment.id)
        # Update serving status based on model response
            if success:
                # Update moderator stats
                stats, created = CommentStats.objects.get_or_create(moderator=request.user)
                stats.is_model_serving = True
                stats.save()

            else:
                # If the model fails, update the is_model_serving flag to False
                stats, created = CommentStats.objects.get_or_create(moderator=request.user)
                stats.is_model_serving = False
                stats.save()
                messages.error(request, "ML Model is not responding. Please check the server.")
                return True
        else:
            stats, created = CommentStats.objects.get_or_create(moderator=request.user)
            stats.is_model_serving = False
            stats.save()
            return False

    user_profile1 = UserProfile.objects.get(user=request.user)
    # Step 1: Determine which posts the user should see
    if request.user.userprofile.role == "admin":
        posts = FacebookPost.objects.filter(fetched_by=request.user)  # Admin sees his fetched posts
    else:
        posts = FacebookPost.objects.filter(fetched_by=user_profile1.assigned_by)  # Moderators see posts fetched by their admin

    # Step 2: Get only comments from these posts
    comments = FacebookComment.objects.filter(post__in=posts)
    deleted_comments = DeletedComment.objects.filter(post__in=posts)
    # Step 3: Filter toxicity parameters based on these comments
    toxic_params = ToxicityParameters.objects.filter(comment__in=comments)

    # Step 4: Count toxicity levels
    total_comments = comments.count() + deleted_comments.count()  # Include deleted ones
    toxic_count = toxic_params.filter(toxic=True).count() + deleted_comments.filter(toxic=True).count()
    non_toxic_count = total_comments - toxic_count

    severe_toxic_count = toxic_params.filter(severe_toxic=True).count() + deleted_comments.filter(severe_toxic=True).count()
    obscene_count = toxic_params.filter(obscene=True).count() + deleted_comments.filter(obscene=True).count()
    threat_count = toxic_params.filter(threat=True).count() + deleted_comments.filter(threat=True).count()
    insult_count = toxic_params.filter(insult=True).count() + deleted_comments.filter(insult=True).count()
    identity_hate_count = toxic_params.filter(identity_hate=True).count() + deleted_comments.filter(identity_hate=True).count()

    # Step 5: Prepare data for Chart.js
    chart_data = {
        "labels": ["Non-Toxic", "Toxic"],
        "data": [non_toxic_count, toxic_count],
        "toxicity_labels": ["Toxic", "Severe Toxic", "Obscene", "Threat", "Insult", "Identity Hate"],
        "toxicity_data": [toxic_count, severe_toxic_count, obscene_count, threat_count, insult_count, identity_hate_count],
    }

    if request.user.userprofile.role == 'admin':  # Admins can see stats for all moderators
        checkModelServing()
        moderators = User.objects.filter(userprofile__role='moderator')  # Get all moderators
        stats_data = []
        for moderator in moderators:
            try:
                stats = moderator.moderator_stats  # Fetch the stats for each moderator
                stats_data.append({
                    'moderator': moderator,
                    'stats': stats
                })
            except CommentStats.DoesNotExist:
                continue  # Skip if no stats exist for a moderator
        context = {
            'is_admin': True,
            'stats_data': stats_data,
            'user': request.user,
        }
    elif request.user.userprofile.role == 'moderator':  # If the user is a moderator, show only their own stats
        try:
            checkModelServing()
            stats = request.user.moderator_stats  # Fetch the current moderator's stats
            context = {
                'is_admin': False,
                'stats': stats,
                'user': request.user,
            }
        except CommentStats.DoesNotExist:
            context = {
                'is_admin': False,
                'stats': None,
                'user': request.user,
            }
    context['chart_data'] = chart_data
    context['user_profile'] = user_profile1
    return render(request, 'users/dashboard.html', context)


# Admin: Add or Update Facebook Access Token and Page ID and assign to Moderators
@login_required
def manage_access_token(request):
    if request.user.userprofile.role != 'admin':
        messages.error(request, "Only Admins can manage access tokens.")
        return redirect('dashboard')

    admin_profile = request.user.userprofile
    assigned_moderators = UserProfile.objects.filter(assigned_by=request.user)

    # Initialize forms
    token_form = AdminTokenForm(instance=admin_profile)
    assign_form = AssignTokenForm()

    if request.method == 'POST':
        # Determine which form was submitted
        if 'update_token' in request.POST:  # Token management form submission
            token_form = AdminTokenForm(request.POST, instance=admin_profile)
            if token_form.is_valid():
                user_profile = token_form.save(commit=False)
                if not user_profile.facebook_access_token or not user_profile.facebook_page_id:
                    messages.error(request, "Both Access Token and Page ID are required.")
                else:
                    user_profile.save()
                    messages.success(request, "Access Token and Page ID updated successfully!")
                return redirect('manage_token')

        elif 'assign_token' in request.POST:  # Token assignment form submission
            assign_form = AssignTokenForm(request.POST)
            if assign_form.is_valid():
                moderator = assign_form.cleaned_data['moderator']
                moderator_profile = moderator.userprofile
                moderator_profile.facebook_access_token = admin_profile.facebook_access_token
                moderator_profile.facebook_page_id = admin_profile.facebook_page_id
                moderator_profile.assigned_by = request.user
                moderator_profile.token_active = True
                moderator_profile.save()
                messages.success(request, f"Token and Page ID assigned to {moderator.username}")
                return redirect('manage_token')
    return render(request, 'users/manage_token.html', {
        'token_form': token_form,
        'assign_form': assign_form,
        'admin_profile': admin_profile,
        'assigned_moderators': assigned_moderators,
    })

# Admin: Assign Token to a Moderator
@login_required
def assign_token(request):
    if request.user.userprofile.role != 'admin':
        messages.error(request, "Only Admins can assign tokens.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = AssignTokenForm(request.POST)
        if form.is_valid():
            moderator = form.cleaned_data['moderator']
            moderator_profile = moderator.userprofile
            moderator_profile.facebook_access_token = request.user.userprofile.facebook_access_token
            moderator_profile.assigned_by = request.user
            moderator_profile.token_active = True
            moderator_profile.save()
            messages.success(request, f"Token and Page ID assigned to {moderator.username}")
            return redirect('manage_token')
    else:
        form = AssignTokenForm()

    return render(request, 'users/assign_token.html', {'form': form})

@login_required
def remove_moderator(request, moderator_id):
    if request.user.userprofile.role != 'admin':
        messages.error(request, "Only Admins can remove moderators.")
        return redirect('manage_token')

    # Get the moderator's profile and ensure it was assigned by the current admin
    moderator_profile = get_object_or_404(UserProfile, user_id=moderator_id, assigned_by=request.user)

    # Reset the moderator's token and assignment
    moderator_profile.facebook_access_token = None
    moderator_profile.facebook_page_id = None
    moderator_profile.assigned_by = None
    moderator_profile.token_active = False
    moderator_profile.save()

    messages.success(request, f"Moderator {moderator_profile.user.username} has been removed successfully.")
    return redirect('manage_token')