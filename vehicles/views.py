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
    url = f"{api_base}/trade/vehicles/mot-tests?registration={registration}"

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
