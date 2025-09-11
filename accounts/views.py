from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from .forms import CustomUserCreationForm, CustomLoginForm, ProfileUpdateForm
from .models import FarmerProfile, BuyerProfile

@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile based on user type
            if user.user_type == 'farmer':
                FarmerProfile.objects.create(user=user)
            else:
                BuyerProfile.objects.create(user=user)
            
            login(request, user)
            messages.success(request, f'Welcome to Online Santha! Your {user.get_user_type_display()} account has been created.')
            return redirect('dashboard:home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@never_cache
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect(next_url)
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('common:home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})
