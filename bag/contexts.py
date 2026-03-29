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

    for bag_key, item_data in bag.items():
        service_id = item_data.get('service_id')
        quantity = item_data.get('quantity', 1)
        reg = item_data.get('reg', 'N/A')

        service = get_object_or_404(Service, pk=service_id)
        total += quantity * service.base_price
        service_count += quantity
        bag_items.append({
            'bag_key': bag_key,
            'quantity': quantity,
            'service': service,
            'subtotal': quantity * service.base_price,
            'reg': reg,
        })

    context = {
        'bag_items': bag_items,
        'total': total,
        'service_count': service_count,
    }

    return context