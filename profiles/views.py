from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm


@login_required
def profile(request):
    """Display the user's profile."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'profile updated successfully!')
    else:
        form = UserProfileForm(instance=user_profile)

    template = 'profiles/profile.html'
    context = {
        'profile': user_profile,
        'form': form,
    }

    return render(request, template, context)