from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date
import requests
import os


def format_date(date_string):
    """
    Convert API date strings to dd/mm/yyyy format.
    """
    if not date_string:
        return None
    try:
        if 'T' in date_string:
            dt = datetime.strptime(date_string[:10], '%Y-%m-%d')
        else:
            dt = datetime.strptime(date_string, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except ValueError:
        return date_string


def format_mileage(value):
    """
    Format mileage with commas e.g. 103449 -> 103,449
    """
    if not value:
        return None
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


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

    # calculate mot days remaining/overdue
    mot_days_text = ''
    mot_expiry = dvla.get('motExpiryDate')
    if mot_expiry:
        try:
            expiry_date = datetime.strptime(mot_expiry, '%Y-%m-%d').date()
            delta = (expiry_date - date.today()).days
            if delta > 0:
                mot_days_text = f"{delta} days remaining"
            elif delta == 0:
                mot_days_text = "expires today"
            else:
                mot_days_text = f"{abs(delta)} days overdue"
        except ValueError:
            mot_days_text = ''

    # calculate tax days remaining/overdue
    tax_days_text = ''
    tax_due = dvla.get('taxDueDate')
    if tax_due:
        try:
            due_date = datetime.strptime(tax_due, '%Y-%m-%d').date()
            delta = (due_date - date.today()).days
            if delta > 0:
                tax_days_text = f"{delta} days remaining"
            elif delta == 0:
                tax_days_text = "due today"
            else:
                tax_days_text = f"{abs(delta)} days overdue"
        except ValueError:
            tax_days_text = ''

    # calculate how long current keeper has had the car
    v5c_days_text = ''
    v5c_date = dvla.get('dateOfLastV5CIssued')
    if v5c_date:
        try:
            issued_date = datetime.strptime(v5c_date, '%Y-%m-%d').date()
            delta = (date.today() - issued_date).days
            years = delta // 365
            months = (delta % 365) // 30
            if years > 0 and months > 0:
                v5c_days_text = (
                    f"{years} year{'s' if years != 1 else ''}, "
                    f"{months} month{'s' if months != 1 else ''}"
                )
            elif years > 0:
                v5c_days_text = f"{years} year{'s' if years != 1 else ''}"
            else:
                v5c_days_text = f"{months} month{'s' if months != 1 else ''}"
        except ValueError:
            v5c_days_text = ''

    # format dates for display
    if dvla.get('motExpiryDate'):
        dvla['motExpiryDateFormatted'] = format_date(dvla['motExpiryDate'])
    if dvla.get('taxDueDate'):
        dvla['taxDueDateFormatted'] = format_date(dvla['taxDueDate'])
    if dvla.get('dateOfLastV5CIssued'):
        dvla['v5cDateFormatted'] = format_date(dvla['dateOfLastV5CIssued'])

    # format mot test dates and mileage, sort defects
    for test in mot_tests:
        test['completedDateFormatted'] = format_date(
            test.get('completedDate', '')
        )
        if test.get('expiryDate'):
            test['expiryDateFormatted'] = format_date(test['expiryDate'])
        if test.get('odometerValue'):
            test['mileageFormatted'] = format_mileage(
                test['odometerValue']
            )
        # sort defects: majors first, then advisories
        if test.get('defects'):
            major_types = ['DANGEROUS', 'MAJOR', 'FAIL', 'PRS']
            majors = [
                d for d in test['defects'] if d.get('type') in major_types
            ]
            advisories = [
                d for d in test['defects'] if d.get('type') not in major_types
            ]
            test['defects'] = majors + advisories

    context = {
        'dvla': dvla,
        'model': model,
        'mot_tests': mot_tests,
        'mot_days_text': mot_days_text,
        'tax_days_text': tax_days_text,
        'v5c_days_text': v5c_days_text,
    }

    return render(request, 'vehicles/vehicle_detail.html', context)