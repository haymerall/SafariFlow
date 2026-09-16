from apps.crm.models import Lead, LeadStatus
from .services import (
    get_company_admin_dashboard,
    get_tour_consultant_dashboard,
    get_finance_officer_dashboard,
)
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.crm.models import Customer, Inquiry, InquiryStatus
from apps.finance.models import Invoice, InvoiceStatus, Payment
from apps.organizations.models import Organization
from apps.tours.models import Booking, BookingStatus

from .services import get_company_admin_dashboard


User = get_user_model()


class CompanyAdminDashboardServiceTests(TestCase):
    def setUp(self):
        self.organization_a = Organization.objects.create(
            name="KLM Kenya Safaris",
            domain="klm.example.com",
        )

        self.organization_b = Organization.objects.create(
            name="Other Safari Company",
            domain="other.example.com",
        )

        self.admin_a = User.objects.create_user(
            username="admin_a",
            password="StrongPassword123!",
            organization=self.organization_a,
            role=UserRole.COMPANY_ADMIN,
        )

        self.customer_a = Customer.objects.create(
            organization=self.organization_a,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        self.customer_b = Customer.objects.create(
            organization=self.organization_b,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )

        Inquiry.objects.create(
            organization=self.organization_a,
            status=InquiryStatus.NEW,
            destination_interest="Masai Mara",
        )

        Inquiry.objects.create(
            organization=self.organization_b,
            status=InquiryStatus.NEW,
            destination_interest="Amboseli",
        )

        self.booking_a = Booking.objects.create(
            organization=self.organization_a,
            customer=self.customer_a,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 5),
            total_passengers=2,
            status=BookingStatus.CONFIRMED,
            total_price=Decimal("3000.00"),
        )

        self.booking_b = Booking.objects.create(
            organization=self.organization_b,
            customer=self.customer_b,
            start_date=date(2026, 12, 10),
            end_date=date(2026, 12, 14),
            total_passengers=2,
            status=BookingStatus.CONFIRMED,
            total_price=Decimal("4000.00"),
        )

        self.invoice_a = Invoice.objects.create(
            organization=self.organization_a,
            booking=self.booking_a,
            amount_due=Decimal("3000.00"),
            status=InvoiceStatus.SENT,
        )

        self.invoice_b = Invoice.objects.create(
            organization=self.organization_b,
            booking=self.booking_b,
            amount_due=Decimal("4000.00"),
            status=InvoiceStatus.SENT,
        )

        Payment.objects.create(
            organization=self.organization_a,
            invoice=self.invoice_a,
            payment_date=date(2026, 9, 1),
            amount_paid=Decimal("1000.00"),
        )

        Payment.objects.create(
            organization=self.organization_b,
            invoice=self.invoice_b,
            payment_date=date(2026, 9, 2),
            amount_paid=Decimal("2000.00"),
        )

        Invoice.objects.create(
            organization=self.organization_a,
            booking=self.booking_a,
            amount_due=Decimal("500.00"),
            status=InvoiceStatus.OVERDUE,
        )

        self.client = APIClient()

    def test_company_admin_dashboard_returns_organization_metrics(self):
        dashboard = get_company_admin_dashboard(self.admin_a)

        self.assertEqual(dashboard["total_customers"], 1)
        self.assertEqual(dashboard["new_inquiries"], 1)
        self.assertEqual(dashboard["active_bookings"], 1)
        self.assertEqual(
            dashboard["total_invoiced"],
            Decimal("3500.00"),
        )
        self.assertEqual(
            dashboard["total_paid"],
            Decimal("1000.00"),
        )
        self.assertEqual(
            dashboard["outstanding_amount"],
            Decimal("2500.00"),
        )
        self.assertEqual(dashboard["overdue_invoices"], 1)

    def test_company_admin_dashboard_excludes_other_organizations(self):
        dashboard = get_company_admin_dashboard(self.admin_a)

        self.assertEqual(dashboard["total_customers"], 1)
        self.assertEqual(dashboard["new_inquiries"], 1)
        self.assertEqual(dashboard["active_bookings"], 1)
        self.assertEqual(
            dashboard["total_invoiced"],
            Decimal("3500.00"),
        )
        self.assertEqual(
            dashboard["total_paid"],
            Decimal("1000.00"),
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_company_admin_can_access_dashboard(self):
        self.client.force_authenticate(user=self.admin_a)

        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["role"],
            UserRole.COMPANY_ADMIN,
        )

        self.assertEqual(
            response.data["organization"]["name"],
            "KLM Kenya Safaris",
        )

        self.assertEqual(
            response.data["metrics"]["total_customers"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["total_invoiced"],
            Decimal("3500.00"),
        )

        self.assertEqual(
            response.data["metrics"]["total_paid"],
            Decimal("1000.00"),
        )

    def test_unsupported_role_receives_forbidden_response(self):
        user = User.objects.create_user(
            username="customer_a",
            password="StrongPassword123!",
            organization=self.organization_a,
            role=UserRole.CUSTOMER,
        )

        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_dashboard_endpoint_does_not_expose_other_organization_data(self):
        self.client.force_authenticate(user=self.admin_a)

        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(
            response.data["metrics"]["total_customers"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["new_inquiries"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["active_bookings"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["total_invoiced"],
            Decimal("3500.00"),
        )

        self.assertNotEqual(
            response.data["metrics"]["total_invoiced"],
            Decimal("7500.00"),
        )
class TourConsultantDashboardServiceTests(TestCase):
    def setUp(self):
        self.organization_a = Organization.objects.create(
            name="KLM Kenya Safaris",
            domain="klm.example.com",
        )

        self.organization_b = Organization.objects.create(
            name="Other Safari Company",
            domain="other.example.com",
        )

        self.consultant_a = User.objects.create_user(
            username="consultant_a",
            password="StrongPassword123!",
            organization=self.organization_a,
            role=UserRole.TOUR_CONSULTANT,
        )

        self.admin_a = User.objects.create_user(
            username="admin_a",
            password="StrongPassword123!",
            organization=self.organization_a,
            role=UserRole.COMPANY_ADMIN,
        )

        self.customer_a = Customer.objects.create(
            organization=self.organization_a,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        self.customer_b = Customer.objects.create(
            organization=self.organization_b,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )

        Lead.objects.create(
            organization=self.organization_a,
            first_name="Alice",
            last_name="Walker",
            status=LeadStatus.QUALIFIED,
        )

        Lead.objects.create(
            organization=self.organization_a,
            first_name="Brian",
            last_name="Otieno",
            status=LeadStatus.NEW,
        )

        Lead.objects.create(
            organization=self.organization_b,
            first_name="Charles",
            last_name="Mwangi",
            status=LeadStatus.QUALIFIED,
        )

        Inquiry.objects.create(
            organization=self.organization_a,
            status=InquiryStatus.NEW,
            destination_interest="Masai Mara",
        )

        Inquiry.objects.create(
            organization=self.organization_a,
            status=InquiryStatus.QUOTED,
            destination_interest="Amboseli",
        )

        Inquiry.objects.create(
            organization=self.organization_b,
            status=InquiryStatus.NEW,
            destination_interest="Tsavo",
        )

        Booking.objects.create(
            organization=self.organization_a,
            customer=self.customer_a,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 5),
            total_passengers=2,
            status=BookingStatus.CONFIRMED,
            total_price=Decimal("3000.00"),
        )

        Booking.objects.create(
            organization=self.organization_a,
            customer=self.customer_a,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 5),
            total_passengers=2,
            status=BookingStatus.PENDING,
            total_price=Decimal("2500.00"),
        )

        Booking.objects.create(
            organization=self.organization_b,
            customer=self.customer_b,
            start_date=date(2026, 12, 10),
            end_date=date(2026, 12, 14),
            total_passengers=2,
            status=BookingStatus.CONFIRMED,
            total_price=Decimal("4000.00"),
        )

    def test_tour_consultant_dashboard_returns_correct_metrics(self):
        dashboard = get_tour_consultant_dashboard(
            self.consultant_a
        )

        self.assertEqual(
            dashboard["new_inquiries"],
            1,
        )

        self.assertEqual(
            dashboard["qualified_leads"],
            1,
        )

        self.assertEqual(
            dashboard["active_bookings"],
            2,
        )

        self.assertEqual(
            dashboard["upcoming_bookings"],
            2,
        )

    def test_tour_consultant_dashboard_excludes_other_organizations(self):
        dashboard = get_tour_consultant_dashboard(
            self.consultant_a
        )

        self.assertEqual(
            dashboard["qualified_leads"],
            1,
        )

        self.assertEqual(
            dashboard["new_inquiries"],
            1,
        )

        self.assertEqual(
            dashboard["active_bookings"],
            2,
        )

        self.assertNotEqual(
            dashboard["qualified_leads"],
            2,
        )

        self.assertNotEqual(
            dashboard["new_inquiries"],
            2,
        )

        self.assertNotEqual(
            dashboard["active_bookings"],
            3,
        )

    def test_non_tour_consultant_cannot_access_tour_consultant_dashboard(self):
        with self.assertRaises(PermissionError):
            get_tour_consultant_dashboard(self.admin_a)
    def test_tour_consultant_can_access_dashboard_api(self):
        client = APIClient()
        client.force_authenticate(user=self.consultant_a)

        response = client.get("/api/v1/dashboard/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["role"],
            UserRole.TOUR_CONSULTANT,
        )

        self.assertEqual(
            response.data["organization"]["name"],
            "KLM Kenya Safaris",
        )

        self.assertEqual(
            response.data["metrics"]["new_inquiries"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["qualified_leads"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["active_bookings"],
            2,
        )

        self.assertEqual(
            response.data["metrics"]["upcoming_bookings"],
            2,
        )
class FinanceOfficerDashboardServiceTests(TestCase):
    def setUp(self):
        self.organization_a = Organization.objects.create(
            name="KLM Kenya Safaris",
            domain="klm-finance.example.com",
        )

        self.organization_b = Organization.objects.create(
            name="Other Safari Company",
            domain="other-finance.example.com",
        )

        self.finance_officer_a = User.objects.create_user(
            username="finance_a",
            password="StrongPassword123!",
            organization=self.organization_a,
            role=UserRole.FINANCE_OFFICER,
        )

        self.admin_a = User.objects.create_user(
            username="admin_finance_a",
            password="StrongPassword123!",
            organization=self.organization_a,
            role=UserRole.COMPANY_ADMIN,
        )

        self.customer_a = Customer.objects.create(
            organization=self.organization_a,
            first_name="John",
            last_name="Finance",
        )

        self.customer_b = Customer.objects.create(
            organization=self.organization_b,
            first_name="Jane",
            last_name="Finance",
        )

        self.booking_a = Booking.objects.create(
            organization=self.organization_a,
            customer=self.customer_a,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 5),
            total_passengers=2,
            status=BookingStatus.CONFIRMED,
            total_price=Decimal("3000.00"),
        )

        self.booking_b = Booking.objects.create(
            organization=self.organization_b,
            customer=self.customer_b,
            start_date=date(2026, 12, 10),
            end_date=date(2026, 12, 14),
            total_passengers=2,
            status=BookingStatus.CONFIRMED,
            total_price=Decimal("4000.00"),
        )

        self.invoice_a = Invoice.objects.create(
            organization=self.organization_a,
            booking=self.booking_a,
            amount_due=Decimal("3000.00"),
            status=InvoiceStatus.SENT,
        )

        Invoice.objects.create(
            organization=self.organization_a,
            booking=self.booking_a,
            amount_due=Decimal("500.00"),
            status=InvoiceStatus.PAID,
        )

        Invoice.objects.create(
            organization=self.organization_a,
            booking=self.booking_a,
            amount_due=Decimal("750.00"),
            status=InvoiceStatus.OVERDUE,
        )

        self.invoice_b = Invoice.objects.create(
            organization=self.organization_b,
            booking=self.booking_b,
            amount_due=Decimal("4000.00"),
            status=InvoiceStatus.SENT,
        )

        Payment.objects.create(
            organization=self.organization_a,
            invoice=self.invoice_a,
            payment_date=date(2026, 9, 10),
            amount_paid=Decimal("1000.00"),
        )

        Payment.objects.create(
            organization=self.organization_b,
            invoice=self.invoice_b,
            payment_date=date(2026, 9, 11),
            amount_paid=Decimal("2000.00"),
        )
    def test_finance_officer_can_access_dashboard_api(self):
        client = APIClient()
        client.force_authenticate(user=self.finance_officer_a)

        response = client.get("/api/v1/dashboard/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["role"],
            UserRole.FINANCE_OFFICER,
        )

        self.assertEqual(
            response.data["organization"]["name"],
            "KLM Kenya Safaris",
        )

        self.assertEqual(
            response.data["metrics"]["total_invoices"],
            3,
        )

        self.assertEqual(
            response.data["metrics"]["paid_invoices"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["overdue_invoices"],
            1,
        )

        self.assertEqual(
            response.data["metrics"]["total_invoiced"],
            Decimal("4250.00"),
        )

        self.assertEqual(
            response.data["metrics"]["total_paid"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            response.data["metrics"]["outstanding_amount"],
            Decimal("3250.00"),
        )

    def test_finance_officer_dashboard_returns_correct_metrics(self):
        dashboard = get_finance_officer_dashboard(
            self.finance_officer_a
        )

        self.assertEqual(
            dashboard["total_invoices"],
            3,
        )

        self.assertEqual(
            dashboard["paid_invoices"],
            1,
        )

        self.assertEqual(
            dashboard["overdue_invoices"],
            1,
        )

        self.assertEqual(
            dashboard["total_invoiced"],
            Decimal("4250.00"),
        )

        self.assertEqual(
            dashboard["total_paid"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            dashboard["outstanding_amount"],
            Decimal("3250.00"),
        )

    def test_finance_officer_dashboard_excludes_other_organizations(self):
        dashboard = get_finance_officer_dashboard(
            self.finance_officer_a
        )

        self.assertEqual(
            dashboard["total_invoices"],
            3,
        )

        self.assertEqual(
            dashboard["total_invoiced"],
            Decimal("4250.00"),
        )

        self.assertEqual(
            dashboard["total_paid"],
            Decimal("1000.00"),
        )

        self.assertNotEqual(
            dashboard["total_invoices"],
            4,
        )

        self.assertNotEqual(
            dashboard["total_invoiced"],
            Decimal("8250.00"),
        )

        self.assertNotEqual(
            dashboard["total_paid"],
            Decimal("3000.00"),
        )

    def test_non_finance_officer_cannot_access_finance_dashboard(self):
        with self.assertRaises(PermissionError):
            get_finance_officer_dashboard(self.admin_a)
