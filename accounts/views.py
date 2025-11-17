"""
Accounts App Views - User Authentication and Profile Management
Reference: https://docs.djangoproject.com/en/5.2/topics/auth/
Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/auth/views/
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CustomPasswordChangeForm
from .models import UserProfile


@require_http_methods(["GET", "POST"])
def register(request):
    """
    User registration view
    Reference: https://docs.djangoproject.com/en/5.2/topics/auth/default/#creating-users
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view
    Reference: https://docs.djangoproject.com/en/5.2/topics/auth/default/#how-to-log-a-user-in
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    User logout view
    Reference: https://docs.djangoproject.com/en/5.2/topics/auth/default/#how-to-log-a-user-out
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):
    """
    User profile view - display profile information
    Reference: https://docs.djangoproject.com/en/5.2/topics/auth/
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    blog_posts = request.user.blog_posts.filter(status='published').count()
    total_likes = sum(post.likes_count for post in request.user.blog_posts.all())
    total_comments = sum(post.comments_count for post in request.user.blog_posts.all())

    context = {
        'profile': profile,
        'user': request.user,
        'blog_posts': blog_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'is_own_profile': True,
    }
    return render(request, 'accounts/profile.html', context)


def profile_detail(request, username):
    """
    Display a specific user's profile view (public profile)
    Reference: https://docs.djangoproject.com/en/5.2/topics/auth/
    """
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    blog_posts = user.blog_posts.filter(status='published').count()
    total_likes = sum(post.likes_count for post in user.blog_posts.filter(status='published'))
    total_comments = sum(post.comments_count for post in user.blog_posts.filter(status='published'))
    
    # Check if viewing own profile or someone else's
    is_own_profile = request.user.is_authenticated and request.user == user

    context = {
        'profile': profile,
        'user': user,
        'blog_posts': blog_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'is_own_profile': is_own_profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """
    Edit user profile view
    Reference: https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )
        if form.is_valid():
            profile = form.save(commit=False)

            # Update user data
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()

            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def change_password(request):
    """
    Change password view
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/auth/views/#django.contrib.auth.views.PasswordChangeView
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
