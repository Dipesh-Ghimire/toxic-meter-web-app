from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)  # Add first name
    last_name = forms.CharField(max_length=30)   # Add last name
    role = forms.ChoiceField(choices=[('admin', 'Admin'), ('moderator', 'Moderator')])

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']  # Save first name
        user.last_name = self.cleaned_data['last_name']    # Save last name
        if commit:
            user.save()
            role = self.cleaned_data['role']  # Save role in UserProfile
            user.userprofile.role = role
            user.userprofile.save()
        return user



# Login Form
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)