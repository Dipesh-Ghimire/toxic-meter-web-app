from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import AssignTokenForm, UserRegisterForm, UserLoginForm, AdminTokenForm
from django.contrib import messages

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
    return render(request, 'users/dashboard.html', {'user': request.user})

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