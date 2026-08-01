from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission


class IsAuthenticatedOr401(BasePermission):
    message = 'Authentication credentials were not provided.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed(self.message)
        return True


class IsAdminUserOr401(BasePermission):
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed('Authentication credentials were not provided.')
        if not request.user.is_staff:
            raise PermissionDenied(self.message)
        return True
