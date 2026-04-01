from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm


@login_required
def profile(request):
    """Display the user's profile with order history."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    orders = user_profile.orders.all().order_by('-date')

    template = 'profiles/profile.html'
    context = {
        'profile': user_profile,
        'form': form,
        'orders': orders,
    }

    return render(request, template, context)


@login_required
def order_history(request, order_number):
    """Display a past order confirmation."""
    from checkout.models import Order
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(
        request,
        f'this is a past confirmation for order {order_number}.'
    )

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)


@login_required
def delete_account(request):
    """Allow user to delete their account and all related data."""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'your account has been deleted.')
        return redirect('home')

    return redirect('profile')