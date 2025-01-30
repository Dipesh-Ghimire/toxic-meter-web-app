
from django.shortcuts import redirect, render
from django.http import request

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")  # Redirect to the dashboard
    else:
        return redirect("login")  # Redirect to the login page