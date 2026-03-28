from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory


def all_services(request):
    """
    Display all services, with optional category filtering.
    """
    services = Service.objects.all()
    categories = ServiceCategory.objects.all()
    selected_category = None

    if request.GET.get('category'):
        selected_category = get_object_or_404(
            ServiceCategory, name=request.GET['category']
        )
        services = services.filter(category=selected_category)

    context = {
        'services': services,
        'categories': categories,
        'selected_category': selected_category,
    }

    return render(request, 'services/services.html', context)


def service_detail(request, service_id):
    """
    Display details of a single service.
    """
    service = get_object_or_404(Service, pk=service_id)

    context = {
        'service': service,
    }

    return render(request, 'services/service_detail.html', context)