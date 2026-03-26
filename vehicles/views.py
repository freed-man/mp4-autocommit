from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import os


def vehicle_lookup(request):
    """
    Handle reg lookup via DVLA VES API.
    """
    if request.method == 'POST':
        registration = request.POST.get('registration', '').strip().upper()
        registration = registration.replace(' ', '')

        if not registration:
            messages.error(request, 'please enter a registration number.')
            return redirect('home')

        api_key = os.environ.get('DVLA_API_KEY')
        url = 'https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles'
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
        }
        payload = {
            'registrationNumber': registration,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                request.session['vehicle_data'] = data
                return redirect('vehicle_detail')
            elif response.status_code == 404:
                messages.error(
                    request,
                    'vehicle not found. please check the registration.'
                )
            else:
                messages.error(
                    request,
                    'unable to look up vehicle. please try again later.'
                )
        except requests.exceptions.RequestException:
            messages.error(
                request,
                'could not connect to the vehicle lookup service.'
            )

        return redirect('home')

    return redirect('home')