from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from .forms import OrderForm
from .models import Order, OrderLineItem
from services.models import Service
from profiles.models import UserProfile
from bag.contexts import bag_contents

import stripe
import json

@require_POST
def cache_checkout_data(request):
    """Cache checkout data in Stripe PaymentIntent metadata."""
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'username': str(request.user),
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            'sorry, your payment cannot be processed right now.'
        )
        return HttpResponse(content=e, status=400)



def checkout(request):
    """Handle the checkout process."""
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()

            for bag_key, item_data in bag.items():
                try:
                    service = Service.objects.get(
                        id=item_data['service_id']
                    )
                    order_line_item = OrderLineItem(
                        order=order,
                        service=service,
                        vehicle_reg=item_data.get('reg', ''),
                        quantity=item_data['quantity'],
                    )
                    order_line_item.save()
                except Service.DoesNotExist:
                    messages.error(
                        request,
                        'one of the services in your bag was not found.'
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            return redirect(
                reverse('checkout_success', args=[order.order_number])
            )
        else:
            messages.error(
                request,
                'there was an error with your form. please check your details.'
            )
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, 'your bag is empty.')
            return redirect(reverse('services'))

        current_bag = bag_contents(request)
        total = current_bag['total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(
                request,
                'stripe public key is missing.'
            )

        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        return render(request, template, context)


def checkout_success(request, order_number):
    """Handle successful checkouts."""
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

    messages.success(
        request,
        f'order confirmed! your order number is {order_number}.'
    )

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)