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
    reg = request.session.get('vehicle_reg', 'N/A')
    bag = request.session.get('bag', {})

    item_id = str(item_id)

    # create unique key combining service and reg
    bag_key = f"{item_id}_{reg}"

    if bag_key in bag:
        bag[bag_key]['quantity'] += quantity
        messages.success(
            request,
            f'updated {service.name} quantity for {reg}'
        )
    else:
        bag[bag_key] = {
            'service_id': int(item_id),
            'quantity': quantity,
            'reg': reg,
        }
        messages.success(
            request,
            f'added {service.name} for {reg} to your bag'
        )

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of a service in the bag."""
    quantity = int(request.POST.get('quantity', 0))
    bag = request.session.get('bag', {})

    bag_key = str(item_id)

    if bag_key in bag:
        if quantity > 0:
            bag[bag_key]['quantity'] = quantity
            messages.success(request, 'bag updated')
        else:
            del bag[bag_key]
            messages.success(request, 'item removed from bag')

    request.session['bag'] = bag
    return redirect('view_bag')


def remove_from_bag(request, item_id):
    """Remove a service from the bag."""
    bag = request.session.get('bag', {})

    bag_key = str(item_id)

    if bag_key in bag:
        del bag[bag_key]
        messages.success(request, 'item removed from bag')

    request.session['bag'] = bag
    return redirect('view_bag')