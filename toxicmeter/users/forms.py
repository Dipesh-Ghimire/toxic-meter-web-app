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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
            'class': 'bg-gray-900 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        })



# Login Form
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

# Form for Admin to update their token
class AdminTokenForm(forms.ModelForm):
    facebook_access_token = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your Facebook Access Token'
    }))
    facebook_page_id = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your Facebook Page ID'
    }))
    class Meta:
        model = UserProfile
        fields = ['facebook_access_token','facebook_page_id', 'token_active']

# Form for Admin to assign a token to Moderators
class AssignTokenForm(forms.Form):
    moderator = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofile__role='moderator'),
        label="Assign Token To Moderator"
    )
    def __init__(self, *args, **kwargs):
        admin_user = kwargs.pop('admin_user', None)
        super().__init__(*args, **kwargs)

        if admin_user:
            admin_profile = admin_user.userprofile
            if not admin_profile.facebook_access_token or not admin_profile.facebook_page_id:
                raise forms.ValidationError("You must configure both a valid Access Token and Page ID before assigning.")