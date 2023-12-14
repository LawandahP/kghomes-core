import requests
from django.utils.translation import gettext_lazy as _
from utils.utils import logger
from django.conf import settings





    
class UseAuthApi:
    def __init__(self, pathName) -> None:
        self.pathName = pathName

    def fetchUserDetails(self, id):
        api_url = f'{settings.AUTH_BASE_URL}/{self.pathName}/{id}'
        
        response = requests.get(api_url)
        
        if response.ok:
            tenant_data = response.json()
            return tenant_data["data"]["payload"]
        else:
            logger.error("Error when fetching user details")
            raise Exception(_("An error occured while fetching user details"))
    
    def fetchBulkUserDetails(self, ids):
        params = {'ids': ','.join(map(str, ids))}
        api_url = f'{settings.AUTH_BASE_URL}/{self.pathName}/'
        
        response = requests.get(api_url, params=params)
        
        if response.ok:
            tenant_data = response.json()
            return tenant_data["data"]["payload"]
        else:
            logger.error("Error when fetching user details")
            raise Exception(_("An error occured while fetching user details"))
