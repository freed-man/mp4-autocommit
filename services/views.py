from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory


FUEL_TYPE_MAP = {
    'PETROL': ['all', 'petrol', 'petrol_diesel', 'petrol_diesel_hybrid'],
    'DIESEL': ['all', 'diesel', 'petrol_diesel', 'petrol_diesel_hybrid'],
    'HYBRID ELECTRIC': [
        'all', 'hybrid', 'electric_hybrid', 'petrol_diesel_hybrid'
    ],
    'ELECTRICITY': ['all', 'electric', 'electric_hybrid'],
}


def is_service_available(service, vehicle_fuel_type):
    """
    Check if a service is available for the given vehicle fuel type.
    """
    if not vehicle_fuel_type:
        return True
    allowed = FUEL_TYPE_MAP.get(vehicle_fuel_type, ['all'])
    return service.fuel_types in allowed


def all_services(request):
    """
    Display all services, with optional category filtering.
    Services are marked as available or greyed out based on
    the vehicle's fuel type stored in the session.
    """
    services = Service.objects.all()
    categories = ServiceCategory.objects.all()
    selected_category = None
    vehicle_fuel_type = request.session.get('vehicle_fuel_type')
    vehicle_reg = request.session.get('vehicle_reg')

    if request.GET.get('category'):
        selected_category = get_object_or_404(
            ServiceCategory, name=request.GET['category']
        )
        services = services.filter(category=selected_category)

    # mark each service as available or not
    services_with_availability = []
    for service in services:
        services_with_availability.append({
            'service': service,
            'available': is_service_available(
                service, vehicle_fuel_type
            ),
        })

    context = {
        'services': services_with_availability,
        'categories': categories,
        'selected_category': selected_category,
        'vehicle_fuel_type': vehicle_fuel_type,
        'vehicle_reg': vehicle_reg,
    }

    return render(request, 'services/services.html', context)


def service_detail(request, service_id):
    """
    Display details of a single service.
    """
    service = get_object_or_404(Service, pk=service_id)
    vehicle_fuel_type = request.session.get('vehicle_fuel_type')
    available = is_service_available(service, vehicle_fuel_type)

    context = {
        'service': service,
        'available': available,
        'vehicle_fuel_type': vehicle_fuel_type,
    }

    return render(request, 'services/service_detail.html', context)