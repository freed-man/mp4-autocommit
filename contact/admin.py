from django.contrib import admin
from .models import ContactRequest


class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'category', 'read', 'created_on')
    list_filter = ('category', 'read')
    search_fields = ('name', 'email', 'message')


admin.site.register(ContactRequest, ContactRequestAdmin)