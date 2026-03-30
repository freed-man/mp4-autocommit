import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from profiles.models import UserProfile
from services.models import Service


class Order(models.Model):
    """
    Stores a single order with customer details and totals.
    """
    order_number = models.CharField(
        max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    vehicle_reg = models.CharField(max_length=10, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        """Generate a random unique order number using UUID."""
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """Update order total from line items."""
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.save()

    def save(self, *args, **kwargs):
        """Override save to set order number if not set."""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    """
    Individual line item in an order, linking to a service.
    """
    order = models.ForeignKey(
        Order, null=False, blank=False,
        on_delete=models.CASCADE, related_name='lineitems')
    service = models.ForeignKey(
        Service, null=False, blank=False,
        on_delete=models.CASCADE)
    vehicle_reg = models.CharField(max_length=10, blank=True)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """Override save to set lineitem total."""
        self.lineitem_total = self.service.base_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.service.name} on order {self.order.order_number}'