# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.utils.translation import gettext_lazy as _
from apps.core.models import UUIDModel, TimeStampedModel

class Organization(UUIDModel, TimeStampedModel):
    """
    The tenant boundary for SafariFlow. 
    Every company using the SaaS will have an Organization record.
    All business data must belong to an Organization.
    """
    name = models.CharField(_("company name"), max_length=255)
    domain = models.CharField(
        _("domain/subdomain"), 
        max_length=100, 
        unique=True, 
        blank=True, 
        null=True,
        help_text=_("Optional custom domain or subdomain for the company.")
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this organization should be treated as active.")
    )

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ['name']

    def __str__(self):
        return self.name
