from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('profiles.urls'), name='profiles-urls'),
    path('vehicles/', include('vehicles.urls'), name='vehicles-urls'),
    path('services/', include('services.urls'), name='services-urls'),
    path('', include('home.urls'), name='home-urls'),
]