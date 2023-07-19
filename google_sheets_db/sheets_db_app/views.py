import json
import os
import requests
import jwt
from django.shortcuts import render, HttpResponseRedirect
from django.conf import settings
from django.http import HttpResponse
import time

def generate_jwt(credentials):
    credentials_info = json.loads(credentials)

    private_key = credentials_info["private_key"]
    jwt_payload = {
        "iss": credentials_info["client_email"],
        "scope": "https://www.googleapis.com/auth/spreadsheets",
        "aud": "https://accounts.google.com/o/oauth2/token",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }

    jwt_token = jwt.encode(jwt_payload, private_key, algorithm="RS256")
    return jwt_token

def get_access_token(jwt_token):
    token_url = 'https://accounts.google.com/o/oauth2/token'
    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': jwt_token,
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("Error:", response.status_code, response.json())
        return None

def save_user_data(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')

        credentials_file = os.path.join(settings.BASE_DIR, 'sheets-db-393304-5e29ed284bca.json')
        with open(credentials_file) as f:
            credentials = json.load(f)

        jwt_token = generate_jwt(json.dumps(credentials))
        access_token = get_access_token(jwt_token)

        if access_token:
            sheet_url = 'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Sheet1!A1:append?valueInputOption=RAW'
            spreadsheet_id = '1ZPnfULum3dEbnb5_ll2pYRfcyqdOk-D2VWFGSfuVdK4'
            url = sheet_url.format(SPREADSHEET_ID=spreadsheet_id)

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }

            # Construct the request payload (the data to append to the sheet)
            data = {
                'values': [[name, mobile_number]],
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                return HttpResponse("User data saved successfully!")
            else:
                print("Error:", response.status_code, response.json())
        return HttpResponse("User data Error!")
    else:
        return render(request, 'index.html')
