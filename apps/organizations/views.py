from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.permissions import IsOrganizationMember, IsCompanyAdmin
from .serializers import OrganizationSerializer


class MyOrganizationView(APIView):
    """
    GET  /api/v1/organizations/me/ — Retrieve the current org details.
    PUT  /api/v1/organizations/me/ — Update org settings (Company Admin only).
    """

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH'):
            return [IsCompanyAdmin()]
        return [IsOrganizationMember()]

    def get(self, request):
        if not request.user.organization:
            return Response(
                {"detail": "You do not belong to an organization."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrganizationSerializer(request.user.organization)
        return Response(serializer.data)

    def put(self, request):
        serializer = OrganizationSerializer(
            request.user.organization, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
