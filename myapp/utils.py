from django.core.mail import send_mail
import uuid 
from pyotp import random_base32
from mypro.settings import INFOBIP_API_KEY, INFOBIP_BASE_URL
import requests
import random

def send_verification_email(user, verification_token):
    subject = 'Verify your email address for My App'
    message = f'Hi {user.first_name} Click the link to verify your email address: http://localhost:8025/#/verify/{verification_token}'
    send_mail(subject, message, 'your_email_address', [user.email])

def generate_verification_token():
    # Implement your logic to generate a unique verification token (e.g., using libraries like 'django-rest-framework-simplejwt')
    # This is a placeholder, replace with your actual implementation
    return str(uuid.uuid4())

def send_otp(otp, phone_number):
    print(f"Simulating OTP sent: {otp} to {phone_number}")  # For development/testing only

def generate_otp():
    return random.randint(1000, 9999)

def send_otp_via_infobip(phone_number, otp):
    data = {
        'from': 'ServiceSMS',  # Replace with your sender ID
        'to': phone_number,
        'text': 'Your OTP is: {}'.format(otp)
    }
    headers = {'Authorization': 'App {}'.format(INFOBIP_API_KEY)}
    response = requests.post(INFOBIP_BASE_URL, json=data, headers=headers)
    print(response.content)

    if response.status_code == 200:
        return True
    else:
        return False