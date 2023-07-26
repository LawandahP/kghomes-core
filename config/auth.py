import jwt

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

from rest_framework import exceptions

import requests
from utils.utils import logger

class CustomBackend(BaseBackend):
    def authenticate(self, request, token=None):
        # Check if a token is provided
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1] if 'HTTP_AUTHORIZATION' in request.META else None
        
        logger.info("Custom Backed Hit Successfully")

        if not token:
            raise exceptions.AuthenticationFailed('Authentication Failed')

        try:
            decoded_token = jwt.decode(token, settings.SIGNING_KEY, algorithms=['HS256'])

            # Extract user information from the decoded token (e.g., 'user_id' is the key in the payload containing the user's identifier)
            user_id = decoded_token.get('user_id')
            logger.warning(user_id)
            if user_id:
                # Try to retrieve the user with the given user_id
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    res = requests.get('http://backend-auth:8001/api/v1/current_user/', headers=headers)
                    logger.info(res)
                    logger.info("auth hit successfully")
                    user = res.json()
                    
                    if res.status_code == 200:
                        user['data']['payload']['is_authenticated'] = True
                        user = user['data']['payload']
                        return user, None
                    # else:
                    #     raise exceptions.AuthenticationFailed(user)
                    
                except:
                    raise exceptions.AuthenticationFailed("Authentication Credentials not provided.")
            else:
                # If 'user_id' is not present in the token payload, return None.
                raise exceptions.AuthenticationFailed('User ID not found.')

        except jwt.InvalidKeyError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        
        except jwt.ExpiredSignatureError:
            # Token is expired
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            # Token is invalid
            raise exceptions.AuthenticationFailed('Invalid token.')

    
    
    def authenticate_header(self, request):
        # Implement this method even if it's not used in your custom backend.
        # The method is required by Django's authentication backend API.
        return 'Bearer'



