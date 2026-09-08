# pyrefly: ignore [missing-import]
from django.urls import reverse
# pyrefly: ignore [missing-import]
from rest_framework import status
# pyrefly: ignore [missing-import]
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole


class RegisterViewTests(APITestCase):
    def test_register_with_organization_becomes_company_admin(self):
        url = reverse('auth-register')
        response = self.client.post(url, {
            'username': 'founder',
            'email': 'founder@example.com',
            'password': 'password123',
            'organization_name': 'New Outfit',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='founder')
        self.assertEqual(user.role, UserRole.COMPANY_ADMIN)
        self.assertEqual(user.organization.name, 'New Outfit')

    def test_register_without_organization_stays_customer(self):
        url = reverse('auth-register')
        response = self.client.post(url, {
            'username': 'guest',
            'email': 'guest@example.com',
            'password': 'password123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='guest')
        self.assertEqual(user.role, UserRole.CUSTOMER)
        self.assertIsNone(user.organization)
