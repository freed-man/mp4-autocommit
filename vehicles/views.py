from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import os


def get_mot_access_token():
    """
    Get an OAuth2 access token from the DVSA MOT API.
    """
    token_url = os.environ.get('MOT_TOKEN_URL')
    client_id = os.environ.get('MOT_CLIENT_ID')
    client_secret = os.environ.get('MOT_CLIENT_SECRET')
    scope = os.environ.get('MOT_SCOPE')

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope,
    }

    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json().get('access_token')
    except requests.exceptions.RequestException:
        return None

    return None


def get_mot_data(registration):
    """
    Fetch MOT history from the DVSA API using OAuth2 token.
    """
    access_token = get_mot_access_token()
    if not access_token:
        return None

    api_base = os.environ.get('MOT_API_BASE')
    api_key = os.environ.get('MOT_API_KEY')
    url = f"{api_base}/v1/trade/vehicles/registration/{registration}"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-API-Key': api_key,
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        return None

    return None


def vehicle_lookup(request):
    """
    Handle reg lookup via DVLA VES API and DVSA MOT API.
    """
    if request.method == 'POST':
        registration = request.POST.get('registration', '').strip().upper()
        registration = registration.replace(' ', '')

        if not registration:
            messages.error(request, 'please enter a registration number.')
            return redirect('home')

        # call dvla api
        api_key = os.environ.get('DVLA_API_KEY')
        url = os.environ.get('DVLA_API_URL')
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
                dvla_data = response.json()

                # call dvsa api for model and mot history
                mot_data = get_mot_data(registration)

                vehicle_info = {
                    'dvla': dvla_data,
                    'mot': mot_data,
                }

                request.session['vehicle_data'] = vehicle_info
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


def vehicle_detail(request):
    """
    Display vehicle details from the DVLA and DVSA API lookups.
    """
    vehicle_data = request.session.get('vehicle_data')

    if not vehicle_data:
        messages.error(
            request,
            'no vehicle data found. please look up a vehicle first.'
        )
        return redirect('home')

    dvla = vehicle_data.get('dvla', {})
    mot = vehicle_data.get('mot')

    # extract model from mot data if available
    model = None
    mot_tests = []
    if mot and isinstance(mot, dict):
        model = mot.get('model')
        mot_tests = mot.get('motTests', [])
    elif mot and isinstance(mot, list) and len(mot) > 0:
        model = mot[0].get('model')
        mot_tests = mot[0].get('motTests', [])

    context = {
        'dvla': dvla,
        'model': model,
        'mot_tests': mot_tests,
    }

    return render(request, 'vehicles/vehicle_detail.html', context)
