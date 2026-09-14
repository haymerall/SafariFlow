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
class AuthenticationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='securepassword123',
            first_name='Alice',
            last_name='Safari',
            role=UserRole.CUSTOMER,
        )

    def test_valid_login_returns_access_and_refresh_tokens(self):
        url = reverse('auth-token-obtain')

        response = self.client.post(
            url,
            {
                'username': 'alice',
                'password': 'securepassword123',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login_is_rejected(self):
        url = reverse('auth-token-obtain')

        response = self.client.post(
            url,
            {
                'username': 'alice',
                'password': 'wrongpassword',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_refresh_token_returns_new_access_token(self):
        login_url = reverse('auth-token-obtain')

        login_response = self.client.post(
            login_url,
            {
                'username': 'alice',
                'password': 'securepassword123',
            },
            format='json',
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK
        )

        refresh_url = reverse('auth-token-refresh')

        response = self.client.post(
            refresh_url,
            {
                'refresh': login_response.data['refresh'],
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn('access', response.data)

    def test_unauthenticated_me_is_rejected(self):
        url = reverse('auth-me')

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_me_returns_current_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('auth-me')

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data['username'],
            'alice'
        )
        self.assertEqual(
            response.data['role'],
            UserRole.CUSTOMER
        )

    def test_me_cannot_change_role(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('auth-me')

        response = self.client.put(
            url,
            {
                'first_name': 'Alice Updated',
                'role': UserRole.COMPANY_ADMIN,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.role,
            UserRole.CUSTOMER
        )
        self.assertEqual(
            self.user.first_name,
            'Alice Updated'
        )

    def test_me_cannot_change_organization(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('auth-me')

        response = self.client.put(
            url,
            {
                'organization': '00000000-0000-0000-0000-000000000000',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertIsNone(
            self.user.organization
        )
