from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrReadOnly(BasePermission):
    """
    give full access to staff user and read-only access
    to non - staff user
    """

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.method in SAFE_METHODS


class IsAdminUserorWriteOnly(BasePermission):
    """
    give full access to staff user and Write-only access
    to non - staff user
    """

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.method == "POST"
