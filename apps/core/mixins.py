class OrganizationScopedMixin:
    """
    A reusable mixin for DRF ViewSets.

    Automatically scopes all querysets to the requesting user's organization,
    preventing any possibility of cross-tenant data leaks.

    Super Admins (no organization) receive an unfiltered queryset.
    All other authenticated users only see their own organization's data.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Super Admins can see all data across all organizations
        from apps.accounts.models import UserRole
        if user.role == UserRole.SUPER_ADMIN:
            return qs

        # All other users are strictly scoped to their organization
        if user.organization:
            return qs.filter(organization=user.organization)

        # If somehow a user has no org and is not Super Admin, return nothing
        return qs.none()

    def perform_create(self, serializer):
        """
        Automatically sets the organization on new objects to match
        the requesting user's organization. Prevents a user from
        manually specifying a different organization in their request body.
        """
        serializer.save(organization=self.request.user.organization)
