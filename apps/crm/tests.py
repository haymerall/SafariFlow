# pyrefly: ignore [missing-import]
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.crm.models import Customer, Inquiry
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


class CrmTenantIsolationTests(APITestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(name='Savanna Safaris')
        self.org_b = Organization.objects.create(name='Coastal Adventures')

        self.user_a = User.objects.create_user(
            username='alice',
            password='password123',
            organization=self.org_a,
            role=UserRole.COMPANY_ADMIN,
        )

        self.user_b = User.objects.create_user(
            username='bob',
            password='password123',
            organization=self.org_b,
            role=UserRole.COMPANY_ADMIN,
        )

        self.customer_a = Customer.objects.create(
            organization=self.org_a,
            first_name='Alice',
            last_name='Safari',
            email='alice@example.com',
        )

        self.customer_b = Customer.objects.create(
            organization=self.org_b,
            first_name='Bob',
            last_name='Traveler',
            email='bob@example.com',
        )

        self.client.force_authenticate(self.user_a)

    def test_customer_list_is_limited_to_current_organization(self):
        response = self.client.get('/api/v1/crm/customers/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {
            item['id']
            for item in response.data['results']
        }

        self.assertIn(str(self.customer_a.id), returned_ids)
        self.assertNotIn(str(self.customer_b.id), returned_ids)

    def test_customer_from_another_organization_cannot_be_retrieved(self):
        response = self.client.get(
            f'/api/v1/crm/customers/{self.customer_b.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_creation_automatically_uses_current_organization(self):
        response = self.client.post(
            '/api/v1/crm/customers/',
            {
                'first_name': 'New',
                'last_name': 'Customer',
                'email': 'new@example.com',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_customer = Customer.objects.get(id=response.data['id'])

        self.assertEqual(created_customer.organization, self.org_a)

    def test_inquiry_cannot_reference_customer_from_another_organization(self):
        response = self.client.post(
            '/api/v1/crm/inquiries/',
            {
                'customer': str(self.customer_b.id),
                'status': 'NEW',
                'destination_interest': 'Masai Mara',
                'number_of_travelers': 2,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer', response.data)

        self.assertFalse(
            Inquiry.objects.filter(
                customer=self.customer_b
            ).exists()
        )
