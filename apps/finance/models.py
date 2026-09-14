import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel, TimeStampedModel


# ---------------------------------------------------------------------------
# Status & Type Choices
# ---------------------------------------------------------------------------

class InvoiceStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    SENT = 'SENT', _('Sent')
    PAID = 'PAID', _('Paid')
    OVERDUE = 'OVERDUE', _('Overdue')
    CANCELLED = 'CANCELLED', _('Cancelled')


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
    MPESA = 'MPESA', _('M-Pesa')
    CREDIT_CARD = 'CREDIT_CARD', _('Credit Card')
    CASH = 'CASH', _('Cash')
    OTHER = 'OTHER', _('Other')


class DocumentType(models.TextChoices):
    INVOICE = 'INVOICE', _('Invoice')
    RECEIPT = 'RECEIPT', _('Receipt')
    ITINERARY = 'ITINERARY', _('Itinerary')
    VOUCHER = 'VOUCHER', _('Voucher')
    OTHER = 'OTHER', _('Other')


# ---------------------------------------------------------------------------
# Invoice Number
# ---------------------------------------------------------------------------

def generate_invoice_number():
    """Generate a short invoice number."""
    return f"INV-{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------

class Invoice(UUIDModel, TimeStampedModel):
    """
    An invoice issued to a customer for a booking.
    Payments are tracked separately and may be partial.
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='invoices',
    )

    booking = models.ForeignKey(
        'tours.Booking',
        on_delete=models.PROTECT,
        related_name='invoices',
        help_text=_("The booking this invoice relates to."),
    )

    invoice_number = models.CharField(
        _("invoice number"),
        max_length=50,
        default=generate_invoice_number,
        editable=False,
    )

    issue_date = models.DateField(
        _("issue date"),
        auto_now_add=True,
    )

    due_date = models.DateField(
        _("due date"),
        null=True,
        blank=True,
    )

    amount_due = models.DecimalField(
        _("amount due"),
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        _("currency"),
        max_length=10,
        default='USD',
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
    )

    notes = models.TextField(
        _("notes"),
        blank=True,
    )

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")
        ordering = ['-issue_date']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'invoice_number'],
                name='unique_invoice_number_per_org',
            ),
            models.CheckConstraint(
                condition=models.Q(amount_due__gte=0),
                name='invoice_amount_due_non_negative',
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.booking_id and self.booking:
            if self.booking.organization_id != self.organization_id:
                errors['booking'] = _(
                    "The selected booking must belong to the same organization."
                )

        if self.due_date and self.issue_date:
            if self.due_date < self.issue_date:
                errors['due_date'] = _(
                    "The due date cannot be earlier than the issue date."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.invoice_number} — "
            f"{self.booking.customer} "
            f"({self.get_status_display()})"
        )

    @property
    def amount_paid(self):
        """Return the total amount paid against this invoice."""
        return self.payments.aggregate(
            total=models.Sum('amount_paid')
        )['total'] or 0

    @property
    def balance_due(self):
        """Return the remaining unpaid balance."""
        return self.amount_due - self.amount_paid


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

class Payment(UUIDModel, TimeStampedModel):
    """
    A payment record against an invoice.
    Multiple partial payments can exist per invoice.
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='payments',
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text=_("The invoice this payment is for."),
    )

    payment_date = models.DateField(
        _("payment date"),
    )

    amount_paid = models.DecimalField(
        _("amount paid"),
        max_digits=12,
        decimal_places=2,
    )

    payment_method = models.CharField(
        _("payment method"),
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
    )

    reference_number = models.CharField(
        _("reference / transaction number"),
        max_length=100,
        blank=True,
        help_text=_(
            "Bank reference, M-Pesa transaction code, etc."
        ),
    )

    notes = models.TextField(
        _("notes"),
        blank=True,
    )

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
        ordering = ['-payment_date']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_paid__gt=0),
                name='payment_amount_positive',
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.invoice_id and self.invoice:
            if self.invoice.organization_id != self.organization_id:
                errors['invoice'] = _(
                    "The selected invoice must belong to the same organization."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} — "
            f"{self.get_payment_method_display()} — "
            f"{self.amount_paid}"
        )


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document(UUIDModel, TimeStampedModel):
    """
    General-purpose document storage for files associated with
    bookings, invoices, itineraries, vouchers, receipts, etc.
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='documents',
    )

    booking = models.ForeignKey(
        'tours.Booking',
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True,
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True,
    )

    document_type = models.CharField(
        _("document type"),
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )

    title = models.CharField(
        _("title"),
        max_length=255,
    )

    file = models.FileField(
        _("file"),
        upload_to='documents/%Y/%m/',
        help_text=_(
            "Stored under media/documents/YYYY/MM/. "
            "Cloud storage can be added later."
        ),
    )

    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='uploaded_documents',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        ordering = ['-created_at']

    def clean(self):
        super().clean()

        errors = {}

        if self.booking_id and self.booking:
            if self.booking.organization_id != self.organization_id:
                errors['booking'] = _(
                    "The selected booking must belong to the same organization."
                )

        if self.invoice_id and self.invoice:
            if self.invoice.organization_id != self.organization_id:
                errors['invoice'] = _(
                    "The selected invoice must belong to the same organization."
                )

        if self.uploaded_by_id and self.uploaded_by:
            if (
                self.uploaded_by.organization_id is not None
                and self.uploaded_by.organization_id != self.organization_id
            ):
                errors['uploaded_by'] = _(
                    "The selected user must belong to the same organization."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.get_document_type_display()}: "
            f"{self.title}"
        )