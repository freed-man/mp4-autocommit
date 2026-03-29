from django.shortcuts import get_object_or_404
from services.models import Service


def bag_contents(request):
    """
    Make bag contents available across all templates.
    """
    bag_items = []
    total = 0
    service_count = 0
    bag = request.session.get('bag', {})

    for item_id, quantity in bag.items():
        service = get_object_or_404(Service, pk=item_id)
        total += quantity * service.base_price
        service_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'service': service,
            'subtotal': quantity * service.base_price,
        })

    context = {
        'bag_items': bag_items,
        'total': total,
        'service_count': service_count,
    }

    return context