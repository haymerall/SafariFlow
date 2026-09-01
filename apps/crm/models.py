from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import UUIDModel, TimeStampedModel

class LeadStatus(models.TextChoices):
    NEW = 'NEW', _('New')
    CONTACTED = 'CONTACTED', _('Contacted')
    QUALIFIED = 'QUALIFIED', _('Qualified')
    LOST = 'LOST', _('Lost')

class InquiryStatus(models.TextChoices):
    NEW = 'NEW', _('New')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    QUOTED = 'QUOTED', _('Quoted')
    BOOKED = 'BOOKED', _('Booked')
    CLOSED = 'CLOSED', _('Closed')


class Lead(UUIDModel, TimeStampedModel):
    """
    A prospective client who has not yet booked a tour.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='leads',
        help_text=_("The organization this lead belongs to.")
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    email = models.EmailField(_("email address"), blank=True, null=True)
    phone_number = models.CharField(_("phone number"), max_length=50, blank=True, null=True)
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW
    )
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("lead")
        verbose_name_plural = _("leads")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Customer(UUIDModel, TimeStampedModel):
    """
    An established client who has booked or completed a tour.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='customers',
        help_text=_("The organization this customer belongs to.")
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    email = models.EmailField(_("email address"), blank=True, null=True)
    phone_number = models.CharField(_("phone number"), max_length=50, blank=True, null=True)
    address = models.TextField(_("address"), blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Inquiry(UUIDModel, TimeStampedModel):
    """
    A specific request for a tour, trip, or package.
    Linked to either a Lead or a Customer.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='inquiries',
        help_text=_("The organization handling this inquiry.")
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        related_name='inquiries',
        null=True,
        blank=True,
        help_text=_("The prospective client who made this inquiry.")
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name='inquiries',
        null=True,
        blank=True,
        help_text=_("The established client who made this inquiry.")
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=InquiryStatus.choices,
        default=InquiryStatus.NEW
    )
    destination_interest = models.CharField(_("destination interest"), max_length=255, blank=True)
    expected_travel_date = models.DateField(_("expected travel date"), null=True, blank=True)
    number_of_travelers = models.PositiveIntegerField(_("number of travelers"), default=1)
    estimated_budget = models.DecimalField(_("estimated budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    special_requirements = models.TextField(_("special requirements"), blank=True)

    class Meta:
        verbose_name = _("inquiry")
        verbose_name_plural = _("inquiries")
        ordering = ['-created_at']

    def __str__(self):
        contact_name = self.customer or self.lead or "Unknown"
        return f"Inquiry from {contact_name} - {self.get_status_display()}"
