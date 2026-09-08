# pyrefly: ignore [missing-import]
from rest_framework import status
# pyrefly: ignore [missing-import]
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.organizations.models import Organization


class CrmInquiryRouteTests(APITestCase):
    def test_inquiries_list_is_reachable(self):
        org = Organization.objects.create(name='Savanna Safaris')
        user = User.objects.create_user(
            username='alice',
            password='password123',
            organization=org,
            role=UserRole.COMPANY_ADMIN,
        )
        self.client.force_authenticate(user)
        response = self.client.get('/api/v1/crm/inquiries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
