import math
import uuid
import requests
from io import BytesIO

import re
import random
import string
import logging
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.db import models


from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from PIL import Image

# from accounts.models import Account


logger = logging.getLogger(__name__)


class CustomUUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20  # Adjust the max length according to your needs
        kwargs['unique'] = True
        kwargs['primary_key'] = True
        kwargs['default'] = self.generate_uuid
        super().__init__(*args, **kwargs)

    def generate_uuid(self):
        unique_id = uuid.uuid4().int >> 64
        return str(unique_id)
    

class GeneratePassword:
    def __init__(self) -> None:
        self.pas = string.ascii_letters + string.digits + string.punctuation
        self.gen = ''.join(random.choices(self.pas , k=8))

    def auto_passwd(self):
        passwd = self.gen
        return passwd
    
    def hash_passwd(self):
        passwd = make_password(self.auto_passwd())
        return passwd

class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of objects to be displayed per page
    page_size_query_param = 'page_size'  # Query parameter to specify the page size
    max_page_size = 100  # Maximum allowed page size



# def get_account(request):
#     try:
#         current_user = User.objects.get(username = request.user)
#         account = Account.objects.get(company_name = current_user.account.company_name)
#     except:
#         return Response({"error": "account not found"})
#     return account

# class GetAccount():
#     def __init__(self, request):
#         self.request = request

#     def get_account(self):
#         try:
#             current_user = User.objects.get(username = self.request.user)
#             account = Account.objects.get(company_name = current_user.account.company_name)
#         except:
#             return Response({"error": "account not found"})
#         return account

#     def handle_err(self):
#         account = self.get_account()
#         if isinstance(account, Response):
#             return account

    
def create_uuid():
    unique_id = uuid.uuid1().int >> 64
    unique_id = str(unique_id)
    return unique_id


def customResponse(**kwargs):
    return Response(
        {
            "data": {
                **kwargs
            }
        }
    )


User = get_user_model()

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP



def phone_number_validator(value):
    pattern = re.compile(r"[\+\d]?(\d{2,3}[-\.\s]??\d{2,3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}")
    if not re.fullmatch(pattern, value):
        raise serializers.ValidationError("An error occured")

def convertDate(date):
    return date.strftime("%a, %B %d, %Y")

def convertToMonth(date):
    return date.strftime("%B, %Y")

def compressImage(file):
    img = Image.open(file)
    thumb_io = BytesIO()
    img.save(thumb_io, "jpeg", quality=80)
    new_image = InMemoryUploadedFile(thumb_io, None, 'foo.jpeg', 'image/jpeg', thumb_io.tell(), None)
    return new_image



def sendRegisterEmail(data):
    url = settings.REGISTER_EMAIL_URL
    payload = {
        "user_type": data["user_type"],
        "name": data["name"],
        "account": data["account"],
        "send_to": data["send_to"],
        "subject": "Welcome To KgHomes",
        "password": data["password"]
    }   

    response = requests.post(url, json=payload)
    return response.json()


if __name__ == '__main__':
    CustomUUIDField()
    sendRegisterEmail()
    convertDate()
    compressImage()
    generateOTP()
    CustomPagination
    GeneratePassword
    logger
