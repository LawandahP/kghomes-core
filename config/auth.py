import jwt

from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.exceptions import APIException

import requests
from utils.utils import logger

from rest_framework.response import Response
from rest_framework import status

class AuthenticationFailedException(Exception):
    pass

class AuthenticationFailedException(APIException):
    status_code = 401
    default_detail = 'Authentication failed.'
    default_code = 'authentication_failed'

class CustomBackend(BaseBackend):
    def authenticate(self, request):
        # Check if a token is provided
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1] if 'HTTP_AUTHORIZATION' in request.META else None

        logger.info("Custom Backed Hit Successfully")
        
        if not token:
            logger.error('Authentication failed: Token not provided.')
            raise AuthenticationFailedException('Authentication failed: Token not provided.')

        try:
            decoded_token = jwt.decode(token, settings.SIGNING_KEY, algorithms=['HS256'])

            # Extract user information from the decoded token (e.g., 'user_id' is the key in the payload containing the user's identifier)
            user_id = decoded_token.get('user_id')
            logger.info({"USER_ID": user_id})
            if user_id:
                # Try to retrieve the user with the given user_id
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    res = requests.get(f"{settings.AUTH_BASE_URL}/users/current/", headers=headers)
                    user = res.json()
                    logger.info(user)
                    if res.status_code == 200:
                        logger.info("USER AUTHENTICATED SUCCESSFULLY")
                        user['is_authenticated'] = True
                        return user, self
                except:
                    logger.error('Failed to get user credentials')
                    raise AuthenticationFailedException('Authentication Credentials are Invalid.')

            else:
                # If 'user_id' is not present in the token payload, return None.
                raise AuthenticationFailedException('User ID not found.')

        except jwt.InvalidKeyError:
            logger.critical('Oops! There was an error decoding the token.')
            raise AuthenticationFailedException('Oops! There was an error decoding the token.')

        except jwt.ExpiredSignatureError:
            # Token is expired
            logger.critical('Oops! Token has expired.')
            raise AuthenticationFailedException('Token has expired. Please login again.')

        except jwt.InvalidTokenError:
            # Token is invalid
            logger.critical('Oops! Invalid Token.')
            raise AuthenticationFailedException('Oops! Looks like your authentication credentials are invalid.')

    def authenticate_header(self, request):
        # Implement this method even if it's not used in your custom backend.
        # The method is required by Django's authentication backend API.
        return 'Bearer'
