# pyrefly: ignore [missing-import]

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.core.mixins import OrganizationScopedMixin
from apps.core.permissions import (
    IsCompanyAdmin,
    IsOrganizationMember,
    IsSuperAdmin,
)
from apps.organizations.models import Organization


User = get_user_model()


class MockRequest:
    def __init__(self, user):
        self.user = user


class MockView:
    pass


class PermissionTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="KLM Kenya Safaris",
            domain="klm-test",
        )

        self.company_admin = User.objects.create_user(
            username="companyadmin",
            password="TestPassword123!",
            organization=self.organization,
            role=UserRole.COMPANY_ADMIN,
        )

        self.staff_user = User.objects.create_user(
            username="staff",
            password="TestPassword123!",
            organization=self.organization,
            role=UserRole.TOUR_CONSULTANT,
        )

        self.super_admin = User.objects.create_user(
            username="superadmin",
            password="TestPassword123!",
            role=UserRole.SUPER_ADMIN,
            organization=None,
        )

        self.no_org_user = User.objects.create_user(
            username="noorg",
            password="TestPassword123!",
            organization=None,
            role=UserRole.TOUR_CONSULTANT,
        )

        self.anonymous_request = MockRequest(
            type(
                "AnonymousUser",
                (),
                {
                    "is_authenticated": False,
                    "role": None,
                    "organization": None,
                },
            )()
        )

    def test_organization_member_allows_company_user(self):
        permission = IsOrganizationMember()

        request = MockRequest(self.staff_user)

        self.assertTrue(
            permission.has_permission(request, MockView())
        )

    def test_organization_member_allows_super_admin(self):
        permission = IsOrganizationMember()

        request = MockRequest(self.super_admin)

        self.assertTrue(
            permission.has_permission(request, MockView())
        )

    def test_organization_member_denies_user_without_organization(self):
        permission = IsOrganizationMember()

        request = MockRequest(self.no_org_user)

        self.assertFalse(
            permission.has_permission(request, MockView())
        )

    def test_organization_member_denies_anonymous_user(self):
        permission = IsOrganizationMember()

        self.assertFalse(
            permission.has_permission(
                self.anonymous_request,
                MockView(),
            )
        )

    def test_company_admin_allows_company_admin(self):
        permission = IsCompanyAdmin()

        request = MockRequest(self.company_admin)

        self.assertTrue(
            permission.has_permission(request, MockView())
        )

    def test_company_admin_allows_super_admin(self):
        permission = IsCompanyAdmin()

        request = MockRequest(self.super_admin)

        self.assertTrue(
            permission.has_permission(request, MockView())
        )

    def test_company_admin_denies_regular_staff(self):
        permission = IsCompanyAdmin()

        request = MockRequest(self.staff_user)

        self.assertFalse(
            permission.has_permission(request, MockView())
        )

    def test_company_admin_denies_anonymous_user(self):
        permission = IsCompanyAdmin()

        self.assertFalse(
            permission.has_permission(
                self.anonymous_request,
                MockView(),
            )
        )

    def test_super_admin_allows_super_admin(self):
        permission = IsSuperAdmin()

        request = MockRequest(self.super_admin)

        self.assertTrue(
            permission.has_permission(request, MockView())
        )

    def test_super_admin_denies_company_admin(self):
        permission = IsSuperAdmin()

        request = MockRequest(self.company_admin)

        self.assertFalse(
            permission.has_permission(request, MockView())
        )

    def test_super_admin_denies_regular_staff(self):
        permission = IsSuperAdmin()

        request = MockRequest(self.staff_user)

        self.assertFalse(
            permission.has_permission(request, MockView())
        )

    def test_super_admin_denies_anonymous_user(self):
        permission = IsSuperAdmin()

        self.assertFalse(
            permission.has_permission(
                self.anonymous_request,
                MockView(),
            )
        )
