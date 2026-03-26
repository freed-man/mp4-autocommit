from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile


@login_required
def profile(request):
    """Display the user's profile."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    template = 'profiles/profile.html'
    context = {
        'profile': user_profile,
    }

    return render(request, template, context)