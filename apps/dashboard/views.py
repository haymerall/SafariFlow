from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole

from .services import (
    get_company_admin_dashboard,
    get_tour_consultant_dashboard,
    get_finance_officer_dashboard,
)


class DashboardView(APIView):
    """
    Main SafariFlow dashboard endpoint.

    The response is determined by the authenticated user's role.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in (
            UserRole.COMPANY_ADMIN,
            UserRole.SUPER_ADMIN,
        ):
            metrics = get_company_admin_dashboard(user)

            organization = (
                user.organization.name
                if user.organization
                else None
            )

            return Response(
                {
                    "role": user.role,
                    "organization": {
                        "id": str(user.organization.id)
                        if user.organization
                        else None,
                        "name": organization,
                    },
                    "metrics": metrics,
                },
                status=status.HTTP_200_OK,
            )

        if user.role == UserRole.TOUR_CONSULTANT:
            metrics = get_tour_consultant_dashboard(user)

            organization = (
                user.organization.name
                if user.organization
                else None
            )

            return Response(
                {
                    "role": user.role,
                    "organization": {
                        "id": str(user.organization.id)
                        if user.organization
                        else None,
                        "name": organization,
                    },
                    "metrics": metrics,
                },
                status=status.HTTP_200_OK,
            )

        if user.role == UserRole.FINANCE_OFFICER:
            metrics = get_finance_officer_dashboard(user)

            organization = (
                user.organization.name
                if user.organization
                else None
            )

            return Response(
                {
                    "role": user.role,
                    "organization": {
                        "id": str(user.organization.id)
                        if user.organization
                        else None,
                        "name": organization,
                    },
                    "metrics": metrics,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": (
                    "Dashboard is not yet implemented "
                    "for your role."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )
