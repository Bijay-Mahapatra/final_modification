# auth/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import RegisterForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({
                'success': True,
                'username': user.username,
                'first_name': user.first_name,
                'profile_image': user.profile_image.url if user.profile_image else None
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data()
        })
    return JsonResponse({'success': False})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({
                'success': True,
                'username': user.username,
                'first_name': user.first_name,
                'profile_image': user.profile_image.url if user.profile_image else None
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data()
        })
    return JsonResponse({'success': False})

@login_required
@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'success': True})

@csrf_exempt
def check_auth(request):
    return JsonResponse({
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
        'first_name': request.user.first_name if request.user.is_authenticated else None,
        'profile_image': request.user.profile_image.url if request.user.is_authenticated and request.user.profile_image else None
    })
