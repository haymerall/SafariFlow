from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
    COMPANY_ADMIN = 'COMPANY_ADMIN', _('Company Admin')
    TOUR_CONSULTANT = 'TOUR_CONSULTANT', _('Tour Consultant')
    FINANCE_OFFICER = 'FINANCE_OFFICER', _('Finance Officer')
    OPERATIONS_MANAGER = 'OPERATIONS_MANAGER', _('Operations Manager')
    DRIVER = 'DRIVER', _('Driver')
    GUIDE = 'GUIDE', _('Guide')
    CUSTOMER = 'CUSTOMER', _('Customer')


class User(AbstractUser):
    """
    Custom User model for SafariFlow.
    Linked to an Organization to provide the foundation for multi-tenancy.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,  # Nullable for system-wide Super Admins who don't belong to a specific company
        blank=True,
        help_text=_("The organization/company this user belongs to.")
    )
    role = models.CharField(
        _("role"),
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        help_text=_("The user's role within the organization.")
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        if self.organization:
            return f"{self.username} ({self.organization.name} - {self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"
