# pyrefly: ignore [missing-import]
from django.core.files.uploadedfile import SimpleUploadedFile

# pyrefly: ignore [missing-import]
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.crm.models import Customer
from apps.organizations.models import Organization
from apps.tours.models import Booking

from .models import Document, Invoice, Payment


class FinanceTenantAPITestCase(APITestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name='Savanna Safaris'
        )
        self.org_b = Organization.objects.create(
            name='Coastal Tours'
        )

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
            email='jane@example.com',
        )

        self.customer_b = Customer.objects.create(
            organization=self.org_b,
            first_name='John',
            last_name='Smith',
            email='john@example.com',
        )

        self.booking_a = Booking.objects.create(
            organization=self.org_a,
            customer=self.customer_a,
            start_date='2026-10-01',
            end_date='2026-10-05',
            total_passengers=2,
            total_price='1500.00',
        )

        self.booking_b = Booking.objects.create(
            organization=self.org_b,
            customer=self.customer_b,
            start_date='2026-11-01',
            end_date='2026-11-05',
            total_passengers=2,
            total_price='1800.00',
        )

        self.invoice_a = Invoice.objects.create(
            organization=self.org_a,
            booking=self.booking_a,
            amount_due='1500.00',
        )

        self.invoice_b = Invoice.objects.create(
            organization=self.org_b,
            booking=self.booking_b,
            amount_due='1800.00',
        )

        self.client.force_authenticate(self.user_a)


class FinanceInvoiceAPITests(FinanceTenantAPITestCase):

    def test_invoice_list_is_scoped_to_current_organization(self):
        response = self.client.get(
            '/api/v1/finance/invoices/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_ids = {
            item['id']
            for item in response.data['results']
        }

        self.assertIn(
            str(self.invoice_a.id),
            returned_ids
        )

        self.assertNotIn(
            str(self.invoice_b.id),
            returned_ids
        )

    def test_foreign_invoice_cannot_be_retrieved(self):
        response = self.client.get(
            f'/api/v1/finance/invoices/{self.invoice_b.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_invoice_creation_uses_current_organization(self):
        response = self.client.post(
            '/api/v1/finance/invoices/',
            {
                'booking': str(self.booking_a.id),
                'amount_due': '1200.00',
                'currency': 'USD',
                'status': 'DRAFT',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        invoice = Invoice.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            invoice.organization,
            self.org_a
        )

    def test_cannot_create_invoice_for_foreign_booking(self):
        response = self.client.post(
            '/api/v1/finance/invoices/',
            {
                'booking': str(self.booking_b.id),
                'amount_due': '1800.00',
                'currency': 'USD',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'booking',
            response.data
        )

    def test_negative_invoice_amount_is_rejected(self):
        response = self.client.post(
            '/api/v1/finance/invoices/',
            {
                'booking': str(self.booking_a.id),
                'amount_due': '-100.00',
                'currency': 'USD',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'amount_due',
            response.data
        )


class FinancePaymentAPITests(FinanceTenantAPITestCase):

    def test_payment_creation_uses_current_organization(self):
        response = self.client.post(
            '/api/v1/finance/payments/',
            {
                'invoice': str(self.invoice_a.id),
                'payment_date': '2026-10-02',
                'amount_paid': '500.00',
                'payment_method': 'MPESA',
                'reference_number': 'MPESA12345',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        payment = Payment.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            payment.organization,
            self.org_a
        )

    def test_cannot_create_payment_for_foreign_invoice(self):
        response = self.client.post(
            '/api/v1/finance/payments/',
            {
                'invoice': str(self.invoice_b.id),
                'payment_date': '2026-11-02',
                'amount_paid': '500.00',
                'payment_method': 'MPESA',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'invoice',
            response.data
        )

    def test_payment_cannot_exceed_invoice_balance(self):
        Payment.objects.create(
            organization=self.org_a,
            invoice=self.invoice_a,
            payment_date='2026-10-02',
            amount_paid='1000.00',
            payment_method='MPESA',
            reference_number='INITIAL1000',
        )

        response = self.client.post(
            '/api/v1/finance/payments/',
            {
                'invoice': str(self.invoice_a.id),
                'payment_date': '2026-10-03',
                'amount_paid': '600.00',
                'payment_method': 'MPESA',
                'reference_number': 'OVERPAY600',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'amount_paid',
            response.data
        )

        self.assertFalse(
            Payment.objects.filter(
                invoice=self.invoice_a,
                reference_number='OVERPAY600',
            ).exists()
        )

    def test_payment_amount_must_be_positive(self):
        response = self.client.post(
            '/api/v1/finance/payments/',
            {
                'invoice': str(self.invoice_a.id),
                'payment_date': '2026-10-02',
                'amount_paid': '0.00',
                'payment_method': 'CASH',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'amount_paid',
            response.data
        )

    def test_invoice_balance_updates_after_payment(self):
        response = self.client.post(
            '/api/v1/finance/payments/',
            {
                'invoice': str(self.invoice_a.id),
                'payment_date': '2026-10-02',
                'amount_paid': '500.00',
                'payment_method': 'MPESA',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.invoice_a.refresh_from_db()

        self.assertEqual(
            self.invoice_a.amount_paid,
            500
        )

        self.assertEqual(
            self.invoice_a.balance_due,
            1000
        )

    def test_payment_list_is_scoped_to_current_organization(self):
        Payment.objects.create(
            organization=self.org_a,
            invoice=self.invoice_a,
            payment_date='2026-10-02',
            amount_paid='500.00',
            payment_method='MPESA',
        )

        Payment.objects.create(
            organization=self.org_b,
            invoice=self.invoice_b,
            payment_date='2026-11-02',
            amount_paid='600.00',
            payment_method='BANK_TRANSFER',
        )

        response = self.client.get(
            '/api/v1/finance/payments/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        invoice_ids = {
            str(item['invoice'])
            for item in response.data['results']
        }

        self.assertIn(
            str(self.invoice_a.id),
            invoice_ids
        )

        self.assertNotIn(
            str(self.invoice_b.id),
            invoice_ids
        )


class FinanceDocumentAPITests(FinanceTenantAPITestCase):

    def test_document_creation_uses_current_organization_and_user(self):
        uploaded_file = SimpleUploadedFile(
            'receipt.pdf',
            b'%PDF-1.4 test receipt content',
            content_type='application/pdf',
         )

        response = self.client.post(
            "/api/v1/finance/documents/",
            {
                "booking": str(self.booking_a.id),
                "invoice": str(self.invoice_a.id),
                "document_type": "RECEIPT",
                "title": "Safari Payment Receipt",
                "file": uploaded_file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        document = Document.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            document.organization,
            self.org_a
        )

        self.assertEqual(
            document.uploaded_by,
            self.user_a
        )

    def test_document_list_is_scoped_to_current_organization(self):
        Document.objects.create(
            organization=self.org_a,
            booking=self.booking_a,
            invoice=self.invoice_a,
            document_type='RECEIPT',
            title='Receipt A',
            uploaded_by=self.user_a,
            file='documents/test/receipt-a.pdf',
        )

        Document.objects.create(
            organization=self.org_b,
            booking=self.booking_b,
            invoice=self.invoice_b,
            document_type='INVOICE',
            title='Invoice B',
            uploaded_by=self.user_b,
            file='documents/test/invoice-b.pdf',
        )

        response = self.client.get(
            '/api/v1/finance/documents/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_ids = {
            item['id']
            for item in response.data['results']
        }

        org_a_document = Document.objects.get(
            organization=self.org_a
        )

        org_b_document = Document.objects.get(
            organization=self.org_b
        )

        self.assertIn(
            str(org_a_document.id),
            returned_ids
        )

        self.assertNotIn(
            str(org_b_document.id),
            returned_ids
        )

    def test_cannot_create_document_for_foreign_booking(self):
        uploaded_file = SimpleUploadedFile(
             'invalid-booking.pdf',
             b'%PDF-1.4 invalid booking test',
             content_type='application/pdf',
    )
        response = self.client.post(
            '/api/v1/finance/documents/',
            {
                'booking': str(self.booking_b.id),
                'invoice': str(self.invoice_a.id),
                'document_type': 'RECEIPT',
                'title': 'Invalid Document',
                'file': uploaded_file,
            },
            format='multipart',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'booking',
            response.data
        )

    def test_cannot_create_document_for_foreign_invoice(self):
        uploaded_file = SimpleUploadedFile(
             'invalid-invoice.pdf',
             b'%PDF-1.4 invalid invoice test',
             content_type='application/pdf',
    )

        response = self.client.post(
            '/api/v1/finance/documents/',
            {
                'booking': str(self.booking_a.id),
                'invoice': str(self.invoice_b.id),
                'document_type': 'INVOICE',
                'file': uploaded_file,
                'title': 'Invalid Invoice Document',
            },
            format='multipart',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'invoice',
            response.data
        )

    def test_foreign_document_cannot_be_retrieved(self):
        document = Document.objects.create(
            organization=self.org_b,
            booking=self.booking_b,
            invoice=self.invoice_b,
            document_type='INVOICE',
            title='Private Invoice',
            uploaded_by=self.user_b,
            file='documents/test/private.pdf',
        )

        response = self.client.get(
            f'/api/v1/finance/documents/{document.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
