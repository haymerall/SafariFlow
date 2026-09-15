# pyrefly: ignore [missing-import]
from django.db import transaction
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.mixins import OrganizationScopedMixin
from apps.core.permissions import IsOrganizationMember

from .models import Invoice, Payment, Document, InvoiceStatus
from .serializers import (
    InvoiceSerializer,
    PaymentSerializer,
    DocumentSerializer,
)


class InvoiceViewSet(
    OrganizationScopedMixin,
    viewsets.ModelViewSet
):
    """
    CRUD API for invoices.

    All invoices are automatically restricted to the
    authenticated user's organization.
    """

    queryset = Invoice.objects.select_related(
        'booking',
        'booking__customer'
    ).all()

    serializer_class = InvoiceSerializer
    permission_classes = (IsOrganizationMember,)

    filter_backends = (
        SearchFilter,
        OrderingFilter,
    )

    search_fields = (
        'invoice_number',
        'booking__customer__first_name',
        'booking__customer__last_name',
    )

    ordering_fields = (
        'issue_date',
        'due_date',
        'amount_due',
        'created_at',
    )


class PaymentViewSet(
    OrganizationScopedMixin,
    viewsets.ModelViewSet
):
    """
    CRUD API for payments.

    Payments are automatically scoped to the authenticated
    user's organization.
    """

    queryset = Payment.objects.select_related(
        'invoice',
        'invoice__booking',
        'invoice__booking__customer'
    ).all()

    serializer_class = PaymentSerializer
    permission_classes = (IsOrganizationMember,)

    filter_backends = (
        SearchFilter,
        OrderingFilter,
    )

    search_fields = (
        'invoice__invoice_number',
        'reference_number',
    )

    ordering_fields = (
        'payment_date',
        'amount_paid',
        'created_at',
    )
    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save(
            organization=self.request.user.organization
        )

        invoice = Invoice.objects.select_for_update().get(
            pk=payment.invoice_id
        )

        if invoice.balance_due == 0:
            invoice.status = InvoiceStatus.PAID
            invoice.save(update_fields=['status', 'updated_at'])

class DocumentViewSet(
    OrganizationScopedMixin,
    viewsets.ModelViewSet
):
    """
    CRUD API for booking and invoice documents.

    Uploaded documents are automatically associated with
    the authenticated user's organization.
    """

    queryset = Document.objects.select_related(
        'booking',
        'invoice',
        'uploaded_by'
    ).all()

    serializer_class = DocumentSerializer
    permission_classes = (IsOrganizationMember,)

    filter_backends = (
        SearchFilter,
        OrderingFilter,
    )

    search_fields = (
        'title',
    )

    ordering_fields = (
        'document_type',
        'title',
        'created_at',
    )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            uploaded_by=self.request.user,
        )
