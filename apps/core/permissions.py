from rest_framework.permissions import BasePermission
from apps.accounts.models import UserRole


class IsOrganizationMember(BasePermission):
    """
    Allows access only to users who belong to an organization.
    Super Admins (no organization) are exempt.
    """
    message = "You must belong to an organization to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        return request.user.organization is not None


class IsCompanyAdmin(BasePermission):
    """
    Allows access only to users with the COMPANY_ADMIN role,
    or Super Admins.
    """
    message = "You must be a Company Admin to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (UserRole.COMPANY_ADMIN, UserRole.SUPER_ADMIN)


class IsSuperAdmin(BasePermission):
    """
    Allows access only to SafariFlow Super Admins.
    """
    message = "You must be a SafariFlow Super Admin to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == UserRole.SUPER_ADMIN
