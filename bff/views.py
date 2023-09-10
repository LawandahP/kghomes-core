
from django.urls import reverse
import requests

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from utils.utils import customResponse, logger
from units.views import AssignUnitToTenant
# Create your views here.

@api_view(['GET'])
def getAssignments(request, id):
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1] if 'HTTP_AUTHORIZATION' in request.META else None
    assignment_instance = AssignUnitToTenant()
    assignments = assignment_instance.get(request, id)

    if assignments.status_code != 200:
        return Response({"error": "Could not retrieve the list of assignments"}, status=assignments.status_code)
    else:
        results = []
        for item in assignments.data['data']['payload']:
            tenant_id = item['tenant']

            headers = {'Authorization': f'Bearer {token}'}
            api_url = f"http://backend-auth:8001/api/v1/tenants/{tenant_id}"

            try:
                # Make an API request to retrieve tenant data
                tenant_response = requests.get(api_url, headers=headers)

                if tenant_response.status_code == 200:
                    # Successfully retrieved tenant data, add it to the results
                    tenant_data = tenant_response.json()
                    del item["tenant"]
                    item['tenant'] = tenant_data["data"]["payload"]  # Add tenant data to the payload item
                    results.append(item)
                else:
                    # Handle errors from the API call
                    return Response({"detail": "Could not retrieve tenant data"}, status=404)
            except requests.exceptions.RequestException as e:
                # Handle request exceptions (e.g., connection error)
                return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"data": {"payload": results}}, status=status.HTTP_200_OK)


    


