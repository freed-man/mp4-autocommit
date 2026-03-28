from django.contrib import admin
from .models import ServiceCategory, Service


class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'base_price', 'fuel_types',
    )
    list_filter = ('category', 'fuel_types',)
    search_fields = ('name', 'description',)
    ordering = ('category', 'name',)


class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'name',)


admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service, ServiceAdmin)