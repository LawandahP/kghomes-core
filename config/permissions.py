from rest_framework.permissions import BasePermission
from utils.utils import logger


class IsRealtor(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user["is_authenticated"]:
            return False

        # Check if the user is a realtor
        return request.user["is_realtor"]

