# pyrefly: ignore [missing-import]
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.crm.models import Customer, Inquiry
from apps.organizations.models import Organization
from apps.tours.models import Booking, Guide, SafariPackage, TourAssignment, Vehicle


class TenantAPITestCase(APITestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(name='Savanna Safaris')
        self.org_b = Organization.objects.create(name='Coastal Tours')

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
            first_name='Jane',
            last_name='Doe',
        )
        self.customer_b = Customer.objects.create(
            organization=self.org_b,
            first_name='John',
            last_name='Smith',
        )

        self.package_a = SafariPackage.objects.create(
            organization=self.org_a,
            name='Masai Mara 3 Days',
            duration_days=3,
            base_price='450.00',
        )
        self.package_b = SafariPackage.objects.create(
            organization=self.org_b,
            name='Tsavo 4 Days',
            duration_days=4,
            base_price='600.00',
        )

        self.vehicle_a = Vehicle.objects.create(
            organization=self.org_a,
            registration_number='KAA-001',
            make='Toyota',
            model='Land Cruiser',
        )
        self.vehicle_b = Vehicle.objects.create(
            organization=self.org_b,
            registration_number='KBB-002',
            make='Nissan',
            model='Patrol',
        )

        self.guide_a = Guide.objects.create(
            organization=self.org_a,
            first_name='Daniel',
            last_name='Ole',
        )
        self.guide_b = Guide.objects.create(
            organization=self.org_b,
            first_name='Peter',
            last_name='Mwangi',
        )


class ToursAPITests(TenantAPITestCase):
    def test_vehicle_list_is_scoped_to_organization(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.get('/api/v1/tours/vehicles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        plates = [
            row['registration_number']
            for row in response.data['results']
        ]

        self.assertEqual(plates, ['KAA-001'])

    def test_cannot_create_booking_for_foreign_customer(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.post(
            '/api/v1/tours/bookings/',
            {
                'customer': str(self.customer_b.id),
                'start_date': '2026-10-01',
                'end_date': '2026-10-05',
                'total_passengers': 2,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer', response.data)

    def test_booking_and_assignment_happy_path(self):
        self.client.force_authenticate(self.user_a)

        booking_response = self.client.post(
            '/api/v1/tours/bookings/',
            {
                'customer': str(self.customer_a.id),
                'package': str(self.package_a.id),
                'start_date': '2026-10-01',
                'end_date': '2026-10-04',
                'total_passengers': 4,
                'total_price': '1800.00',
            },
            format='json',
        )

        self.assertEqual(
            booking_response.status_code,
            status.HTTP_201_CREATED,
        )

        booking_id = booking_response.data['id']

        assignment_response = self.client.post(
            '/api/v1/tours/assignments/',
            {
                'booking': booking_id,
                'guide': str(self.guide_a.id),
                'vehicle': str(self.vehicle_a.id),
            },
            format='json',
        )

        self.assertEqual(
            assignment_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            TourAssignment.objects.filter(
                booking_id=booking_id
            ).exists()
        )

        self.client.force_authenticate(self.user_b)

        hidden = self.client.get(
            f'/api/v1/tours/bookings/{booking_id}/'
        )

        self.assertEqual(
            hidden.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_assignment_rejects_foreign_vehicle(self):
        booking = Booking.objects.create(
            organization=self.org_a,
            customer=self.customer_a,
            start_date='2026-10-01',
            end_date='2026-10-03',
        )

        self.client.force_authenticate(self.user_a)

        response = self.client.post(
            '/api/v1/tours/assignments/',
            {
                'booking': str(booking.id),
                'guide': str(self.guide_a.id),
                'vehicle': str(self.vehicle_b.id),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('vehicle', response.data)

    def test_cannot_create_booking_for_foreign_package(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.post(
            '/api/v1/tours/bookings/',
            {
                'customer': str(self.customer_a.id),
                'package': str(self.package_b.id),
                'start_date': '2026-10-01',
                'end_date': '2026-10-05',
                'total_passengers': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('package', response.data)

    def test_cannot_create_booking_for_foreign_inquiry(self):
        inquiry = Inquiry.objects.create(
            organization=self.org_b,
            customer=self.customer_b,
            destination_interest='Tsavo',
            number_of_travelers=2,
        )

        self.client.force_authenticate(self.user_a)

        response = self.client.post(
            '/api/v1/tours/bookings/',
            {
                'customer': str(self.customer_a.id),
                'inquiry': str(inquiry.id),
                'start_date': '2026-10-01',
                'end_date': '2026-10-05',
                'total_passengers': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('inquiry', response.data)

    def test_assignment_rejects_foreign_guide(self):
        booking = Booking.objects.create(
            organization=self.org_a,
            customer=self.customer_a,
            start_date='2026-10-01',
            end_date='2026-10-03',
        )

        self.client.force_authenticate(self.user_a)

        response = self.client.post(
            '/api/v1/tours/assignments/',
            {
                'booking': str(booking.id),
                'guide': str(self.guide_b.id),
                'vehicle': str(self.vehicle_a.id),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('guide', response.data)

    def test_cannot_access_foreign_vehicle_directly(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.get(
            f'/api/v1/tours/vehicles/{self.vehicle_b.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_access_foreign_package_directly(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.get(
            f'/api/v1/tours/packages/{self.package_b.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_access_foreign_guide_directly(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.get(
            f'/api/v1/tours/guides/{self.guide_b.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_booking_creation_uses_current_organization(self):
        self.client.force_authenticate(self.user_a)

        response = self.client.post(
            '/api/v1/tours/bookings/',
            {
                'customer': str(self.customer_a.id),
                'package': str(self.package_a.id),
                'start_date': '2026-10-01',
                'end_date': '2026-10-05',
                'total_passengers': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        booking = Booking.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            booking.organization,
            self.org_a,
        )
