"""
Permissions for the product API.
"""
from rest_framework import permissions


class DenyPostPermission(permissions.BasePermission):
    """Deny post request for non-staff users."""

    def has_permission(self, request, view):
        if (request.user.is_anonymous) or (not request.user.is_staff):
            return request.method in permissions.SAFE_METHODS

        return True
