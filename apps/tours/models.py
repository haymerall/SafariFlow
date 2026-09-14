from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel, TimeStampedModel


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


class Vehicle(UUIDModel, TimeStampedModel):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    registration_number = models.CharField(
        _("registration number"),
        max_length=50
    )
    make = models.CharField(
        _("make"),
        max_length=100,
        help_text=_("e.g. Toyota")
    )
    model = models.CharField(
        _("model"),
        max_length=100,
        help_text=_("e.g. Land Cruiser")
    )
    capacity = models.PositiveIntegerField(
        _("passenger capacity"),
        default=7
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=VehicleStatus.choices,
        default=VehicleStatus.ACTIVE
    )

    class Meta:
        verbose_name = _("vehicle")
        verbose_name_plural = _("vehicles")
        ordering = ['organization', 'make', 'model']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'registration_number'],
                name='unique_vehicle_registration_per_org'
            )
        ]

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"


class Guide(UUIDModel, TimeStampedModel):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='guides'
    )
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='guide_profile',
        null=True,
        blank=True
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    license_number = models.CharField(
        _("license number"),
        max_length=100,
        blank=True
    )
    languages_spoken = models.CharField(
        _("languages spoken"),
        max_length=255,
        blank=True,
        help_text=_(
            "Comma-separated list, e.g. English, Swahili, French"
        )
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=GuideStatus.choices,
        default=GuideStatus.ACTIVE
    )

    class Meta:
        verbose_name = _("guide")
        verbose_name_plural = _("guides")
        ordering = ['organization', 'last_name', 'first_name']

    def clean(self):
        super().clean()

        if self.user_id and self.user:
            if (
                self.user.organization_id is not None
                and self.user.organization_id != self.organization_id
            ):
                raise ValidationError({
                    'user': _(
                        "The selected user must belong to the same organization."
                    )
                })

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SafariPackage(UUIDModel, TimeStampedModel):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='packages'
    )
    name = models.CharField(
        _("package name"),
        max_length=255
    )
    description = models.TextField(
        _("description"),
        blank=True
    )
    duration_days = models.PositiveIntegerField(
        _("duration (days)"),
        default=1
    )
    base_price = models.DecimalField(
        _("base price"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Base price per person in USD.")
    )
    is_active = models.BooleanField(
        _("active"),
        default=True
    )

    class Meta:
        verbose_name = _("safari package")
        verbose_name_plural = _("safari packages")
        ordering = ['organization', 'name']

    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"


class Booking(UUIDModel, TimeStampedModel):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    customer = models.ForeignKey(
        'crm.Customer',
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    inquiry = models.ForeignKey(
        'crm.Inquiry',
        on_delete=models.SET_NULL,
        related_name='bookings',
        null=True,
        blank=True
    )
    package = models.ForeignKey(
        SafariPackage,
        on_delete=models.SET_NULL,
        related_name='bookings',
        null=True,
        blank=True
    )
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    total_passengers = models.PositiveIntegerField(
        _("total passengers"),
        default=1
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    total_price = models.DecimalField(
        _("total price"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    special_notes = models.TextField(
        _("special notes"),
        blank=True
    )

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        ordering = ['-start_date']

    def clean(self):
        super().clean()

        errors = {}

        if self.customer_id and self.customer:
            if self.customer.organization_id != self.organization_id:
                errors['customer'] = _(
                    "The selected customer must belong to the same organization."
                )

        if self.inquiry_id and self.inquiry:
            if self.inquiry.organization_id != self.organization_id:
                errors['inquiry'] = _(
                    "The selected inquiry must belong to the same organization."
                )

        if self.package_id and self.package:
            if self.package.organization_id != self.organization_id:
                errors['package'] = _(
                    "The selected package must belong to the same organization."
                )

        if self.end_date < self.start_date:
            errors['end_date'] = _(
                "The end date cannot be earlier than the start date."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Booking #{self.id} — {self.customer} ({self.start_date})"


class TourAssignment(UUIDModel, TimeStampedModel):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    guide = models.ForeignKey(
        Guide,
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    notes = models.TextField(
        _("operational notes"),
        blank=True
    )

    class Meta:
        verbose_name = _("tour assignment")
        verbose_name_plural = _("tour assignments")
        ordering = ['booking__start_date']

    def clean(self):
        super().clean()

        errors = {}

        if self.booking_id and self.booking:
            booking_org_id = self.booking.organization_id

            if (
                self.guide_id
                and self.guide
                and self.guide.organization_id != booking_org_id
            ):
                errors['guide'] = _(
                    "The selected guide must belong to the same organization as the booking."
                )

            if (
                self.vehicle_id
                and self.vehicle
                and self.vehicle.organization_id != booking_org_id
            ):
                errors['vehicle'] = _(
                    "The selected vehicle must belong to the same organization as the booking."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.booking} → Guide: {self.guide} | Vehicle: {self.vehicle}"