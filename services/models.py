from django.db import models
from cloudinary.models import CloudinaryField


class ServiceCategory(models.Model):
    """
    Categories for grouping services e.g. Maintenance, Brakes, MOT.
    """
    name = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['name']

    def __str__(self):
        return self.friendly_name

    def get_friendly_name(self):
        return self.friendly_name


class Service(models.Model):
    """
    Individual services offered, linked to a category.
    Fuel types field controls which vehicles can book this service.
    """
    FUEL_TYPE_CHOICES = [
        ('all', 'All Vehicles'),
        ('petrol', 'Petrol Only'),
        ('diesel', 'Diesel Only'),
        ('petrol_diesel', 'Petrol & Diesel'),
        ('petrol_diesel_hybrid', 'Petrol, Diesel & Hybrid'),
        ('electric', 'Electric Only'),
        ('electric_hybrid', 'Electric & Hybrid'),
        ('hybrid', 'Hybrid Only'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name='services')
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    image = CloudinaryField('image', default='placeholder')
    fuel_types = models.CharField(
        max_length=50, choices=FUEL_TYPE_CHOICES, default='all')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name