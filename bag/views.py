from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from services.models import Service


def view_bag(request):
    """Display the shopping bag."""
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """Add a service to the shopping bag."""
    service = get_object_or_404(Service, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')
    bag = request.session.get('bag', {})

    item_id = str(item_id)

    if item_id in bag:
        bag[item_id] += quantity
        messages.success(
            request,
            f'updated {service.name} quantity to {bag[item_id]}'
        )
    else:
        bag[item_id] = quantity
        messages.success(
            request,
            f'added {service.name} to your bag'
        )

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of a service in the bag."""
    service = get_object_or_404(Service, pk=item_id)
    quantity = int(request.POST.get('quantity', 0))
    bag = request.session.get('bag', {})

    item_id = str(item_id)

    if quantity > 0:
        bag[item_id] = quantity
        messages.success(
            request,
            f'updated {service.name} quantity to {bag[item_id]}'
        )
    else:
        bag.pop(item_id, None)
        messages.success(
            request,
            f'removed {service.name} from your bag'
        )

    request.session['bag'] = bag
    return redirect('view_bag')


def remove_from_bag(request, item_id):
    """Remove a service from the bag."""
    service = get_object_or_404(Service, pk=item_id)
    bag = request.session.get('bag', {})

    item_id = str(item_id)

    bag.pop(item_id, None)
    messages.success(
        request,
        f'removed {service.name} from your bag'
    )

    request.session['bag'] = bag
    return redirect('view_bag')