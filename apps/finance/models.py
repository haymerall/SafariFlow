import uuid
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
# Finance Models
# ---------------------------------------------------------------------------

def generate_invoice_number():
    """Generate a unique short invoice number using part of a UUID."""
    return f"INV-{uuid.uuid4().hex[:8].upper()}"


class Invoice(UUIDModel, TimeStampedModel):
    """
    An invoice issued to a customer for a booking.
    This is the source of truth for what the customer owes.
    Payments are tracked separately and can be partial.
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
        help_text=_("The booking this invoice relates to.")
    )
    invoice_number = models.CharField(
        _("invoice number"),
        max_length=50,
        unique=True,
        default=generate_invoice_number,
        editable=False,
    )
    issue_date = models.DateField(_("issue date"), auto_now_add=True)
    due_date = models.DateField(_("due date"), null=True, blank=True)
    amount_due = models.DecimalField(
        _("amount due"), max_digits=12, decimal_places=2
    )
    currency = models.CharField(
        _("currency"), max_length=10, default='USD'
    )
    status = models.CharField(
        _("status"), max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
    )
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.invoice_number} — {self.booking.customer} ({self.get_status_display()})"

    @property
    def amount_paid(self):
        """Sum of all confirmed payments against this invoice."""
        return self.payments.aggregate(
            total=models.Sum('amount_paid')
        )['total'] or 0

    @property
    def balance_due(self):
        """Remaining balance: what is still owed."""
        return self.amount_due - self.amount_paid


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
        help_text=_("The invoice this payment is for.")
    )
    payment_date = models.DateField(_("payment date"))
    amount_paid = models.DecimalField(
        _("amount paid"), max_digits=12, decimal_places=2
    )
    payment_method = models.CharField(
        _("payment method"), max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
    )
    reference_number = models.CharField(
        _("reference / transaction number"),
        max_length=100, blank=True,
        help_text=_("Bank reference, M-Pesa transaction code, etc.")
    )
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.invoice.invoice_number} — {self.get_payment_method_display()} — {self.amount_paid}"


class Document(UUIDModel, TimeStampedModel):
    """
    A general-purpose document store for files associated with
    a booking or invoice (PDFs, itineraries, vouchers, etc.).
    Files are stored using Django's FileField which supports both
    local media storage and can later be swapped to cloud storage.
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
        _("document type"), max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    title = models.CharField(_("title"), max_length=255)
    file = models.FileField(
        _("file"), upload_to='documents/%Y/%m/',
        help_text=_("Stored under media/documents/YYYY/MM/. Swap upload_to for cloud storage later.")
    )
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='uploaded_documents',
        null=True, blank=True,
    )

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()}: {self.title}"
