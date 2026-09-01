from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import UUIDModel, TimeStampedModel


# ---------------------------------------------------------------------------
# Status Choices
# ---------------------------------------------------------------------------

class VehicleStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', _('Active')
    MAINTENANCE = 'MAINTENANCE', _('Under Maintenance')
    RETIRED = 'RETIRED', _('Retired')


class GuideStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', _('Active')
    INACTIVE = 'INACTIVE', _('Inactive')


class BookingStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')


# ---------------------------------------------------------------------------
# Operational Assets
# ---------------------------------------------------------------------------

class Vehicle(UUIDModel, TimeStampedModel):
    """
    A vehicle (4x4, minivan, etc.) owned/operated by a safari company.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='vehicles',
        help_text=_("The organization that owns this vehicle.")
    )
    registration_number = models.CharField(
        _("registration number"), max_length=50, unique=True
    )
    make = models.CharField(_("make"), max_length=100, help_text=_("e.g. Toyota"))
    model = models.CharField(_("model"), max_length=100, help_text=_("e.g. Land Cruiser"))
    capacity = models.PositiveIntegerField(
        _("passenger capacity"), default=7
    )
    status = models.CharField(
        _("status"), max_length=20,
        choices=VehicleStatus.choices,
        default=VehicleStatus.ACTIVE,
    )

    class Meta:
        verbose_name = _("vehicle")
        verbose_name_plural = _("vehicles")
        ordering = ['organization', 'make', 'model']

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"


class Guide(UUIDModel, TimeStampedModel):
    """
    A safari guide or driver employed by a safari company.
    Optionally linked to a User account for system login capability.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='guides',
        help_text=_("The organization this guide works for.")
    )
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='guide_profile',
        null=True,
        blank=True,
        help_text=_("Optional: Link to a system user account.")
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    license_number = models.CharField(_("license number"), max_length=100, blank=True)
    languages_spoken = models.CharField(
        _("languages spoken"), max_length=255, blank=True,
        help_text=_("Comma-separated list, e.g. English, Swahili, French")
    )
    status = models.CharField(
        _("status"), max_length=20,
        choices=GuideStatus.choices,
        default=GuideStatus.ACTIVE,
    )

    class Meta:
        verbose_name = _("guide")
        verbose_name_plural = _("guides")
        ordering = ['organization', 'last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ---------------------------------------------------------------------------
# Safari Packages
# ---------------------------------------------------------------------------

class SafariPackage(UUIDModel, TimeStampedModel):
    """
    A predefined, reusable safari package template offered by a company.
    Used as an optional template when creating a Booking.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='packages',
        help_text=_("The organization offering this package.")
    )
    name = models.CharField(_("package name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    duration_days = models.PositiveIntegerField(_("duration (days)"), default=1)
    base_price = models.DecimalField(
        _("base price"), max_digits=10, decimal_places=2,
        help_text=_("Base price per person in USD.")
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("safari package")
        verbose_name_plural = _("safari packages")
        ordering = ['organization', 'name']

    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"


# ---------------------------------------------------------------------------
# Bookings & Operations
# ---------------------------------------------------------------------------

class Booking(UUIDModel, TimeStampedModel):
    """
    A confirmed or prospective tour booking by a customer.
    Optionally linked to a CRM Inquiry and/or a predefined SafariPackage.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text=_("The organization managing this booking.")
    )
    customer = models.ForeignKey(
        'crm.Customer',
        on_delete=models.PROTECT,
        related_name='bookings',
        help_text=_("The customer making this booking.")
    )
    inquiry = models.ForeignKey(
        'crm.Inquiry',
        on_delete=models.SET_NULL,
        related_name='bookings',
        null=True,
        blank=True,
        help_text=_("The originating inquiry, if applicable.")
    )
    package = models.ForeignKey(
        SafariPackage,
        on_delete=models.SET_NULL,
        related_name='bookings',
        null=True,
        blank=True,
        help_text=_("The predefined package, if applicable (leave blank for custom tours).")
    )
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    total_passengers = models.PositiveIntegerField(_("total passengers"), default=1)
    status = models.CharField(
        _("status"), max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    total_price = models.DecimalField(
        _("total price"), max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text=_("Final agreed price for this booking.")
    )
    special_notes = models.TextField(_("special notes"), blank=True)

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        ordering = ['-start_date']

    def __str__(self):
        return f"Booking #{self.id} — {self.customer} ({self.start_date})"


class TourAssignment(UUIDModel, TimeStampedModel):
    """
    Assigns a guide and vehicle to a specific booking.
    This is the operational link between resources and bookings.
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    guide = models.ForeignKey(
        Guide,
        on_delete=models.PROTECT,
        related_name='assignments',
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='assignments',
    )
    notes = models.TextField(_("operational notes"), blank=True)

    class Meta:
        verbose_name = _("tour assignment")
        verbose_name_plural = _("tour assignments")
        ordering = ['booking__start_date']

    def __str__(self):
        return f"{self.booking} → Guide: {self.guide} | Vehicle: {self.vehicle}"
