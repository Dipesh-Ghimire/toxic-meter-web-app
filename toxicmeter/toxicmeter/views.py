
from django.shortcuts import render
from django.http import request

def home(request):
    return render(request,"layout.html")