from django.urls import path
from . import views

urlpatterns = [
    path('lookup/', views.vehicle_lookup, name='vehicle_lookup'),
]