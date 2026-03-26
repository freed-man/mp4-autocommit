from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    """
    Stores vehicle details retrieved from the DVLA API,
    linked to a registered user.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vehicles")
    registration = models.CharField(max_length=10)
    make = models.CharField(max_length=100)
    colour = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=50)
    engine_capacity = models.IntegerField(blank=True, null=True)
    year_of_manufacture = models.IntegerField()
    mot_status = models.CharField(max_length=50, blank=True)
    mot_expiry = models.DateField(blank=True, null=True)
    tax_status = models.CharField(max_length=50, blank=True)
    tax_due_date = models.DateField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.year_of_manufacture} {self.make} ({self.registration})"
