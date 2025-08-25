from django.test import TestCase

# Create your tests here.
import requests

# 1. Login
login_url = "http://127.0.0.1:8000/api/login/"
login_payload = {
    "username": "admin",  # Example: "admin"
    "password": "KanoNigeria@2025",  # Example: "yourPassword123"
    "token": "123456"                  # If you are using 2FA; otherwise leave blank or skip depending on your view
}

login_response = requests.post(login_url, json=login_payload)

if login_response.status_code == 200:
    access_token = login_response.json().get("access")
    if not access_token:
        print("Access token not found in response.")
        exit()

    print("Login successful!")
    print("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NTk2MTMxMiwiaWF0IjoxNzQ1ODc0OTEyLCJqdGkiOiJiNWJlYzUwYzNhYWM0OTViYTg3NWE4OWZlY2YyM2MxNCIsInVzZXJfaWQiOjJ9.Ib3v5EFYVxZOk0Ye5XiT6361d3Coyt0H6PcaxKFZxJQ","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ1ODc4NTEyLCJpYXQiOjE3NDU4NzQ5MTIsImp0aSI6ImE2M2IwZjVkNzE5NzQ0ODRhZmE0MTQ1Mjc4M2U1YjNkIiwidXNlcl9pZCI6Mn0.PyXtdpuf_69JW3_lSECbhG76MggX6Rm4uXSJx5GV-Qw:", access_token)

    # 2. Access protected endpoint (Generate 2FA QR)
    generate_2fa_url = "http://127.0.0.1:8000/api/generate-2fa/"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    qr_response = requests.get(generate_2fa_url, headers=headers)

    if qr_response.status_code == 200:
        print("2FA QR Info:")
        print(qr_response.json())
    else:
        print("Failed to generate 2FA QR:", qr_response.status_code, qr_response.text)

else:
    print("Login failed:", login_response.status_code, login_response.text)
