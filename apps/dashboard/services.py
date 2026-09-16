from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.crm.models import Customer, Inquiry, InquiryStatus, Lead, LeadStatus
from apps.finance.models import Invoice, Payment, InvoiceStatus
from apps.tours.models import Booking, BookingStatus, Guide, Vehicle, VehicleStatus


User = get_user_model()


def get_user_context(user):
    """
    Return the authenticated user's dashboard context.
    """
    if not user or not user.is_authenticated:
        raise ValueError("Authenticated user is required.")

    return {
        "user": user,
        "role": user.role,
        "organization": user.organization,
        "is_super_admin": user.role == UserRole.SUPER_ADMIN,
    }


def get_organization_filter(user):
    """
    Return a queryset filter appropriate for the user's organization.

    Super Admins operate across the entire platform.
    Organization users are restricted to their organization.
    """
    context = get_user_context(user)

    if context["is_super_admin"]:
        return {}

    if context["organization"] is None:
        raise ValueError(
            "This user must belong to an organization."
        )

    return {
        "organization": context["organization"]
    }


def get_active_booking_statuses():
    """
    Return booking statuses considered active.
    """
    return [
        BookingStatus.PENDING,
        BookingStatus.CONFIRMED,
    ]


def get_upcoming_booking_queryset(user):
    """
    Return upcoming active bookings within the user's scope.
    """
    org_filter = get_organization_filter(user)

    return Booking.objects.filter(
        start_date__gte=timezone.localdate(),
        status__in=get_active_booking_statuses(),
        **org_filter,
    )


def get_financial_summary(user):
    """
    Return organization/platform financial totals.
    """
    org_filter = get_organization_filter(user)

    total_invoiced = (
        Invoice.objects.filter(
            **org_filter
        ).aggregate(
            total=Sum("amount_due")
        )["total"]
        or 0
    )

    total_paid = (
        Payment.objects.filter(
            **org_filter
        ).aggregate(
            total=Sum("amount_paid")
        )["total"]
        or 0
    )

    return {
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding_amount": total_invoiced - total_paid,
        "overdue_invoices": Invoice.objects.filter(
            status=InvoiceStatus.OVERDUE,
            **org_filter,
        ).count(),
    }

def get_tour_consultant_dashboard(user):
    """
    Return sales and CRM metrics for a Tour Consultant.
    """

    context = get_user_context(user)

    if context["role"] != UserRole.TOUR_CONSULTANT:
        raise PermissionError(
            "Tour Consultant dashboard access is required."
        )

    org_filter = get_organization_filter(user)

    return {
        "new_inquiries": Inquiry.objects.filter(
            status=InquiryStatus.NEW,
            **org_filter,
        ).count(),

        "qualified_leads": Lead.objects.filter(
            status=LeadStatus.QUALIFIED,
            **org_filter,
        ).count(),

        "active_bookings": Booking.objects.filter(
            status__in=get_active_booking_statuses(),
            **org_filter,
        ).count(),

        "upcoming_bookings": get_upcoming_booking_queryset(
            user
        ).count(),
    }

def get_company_admin_dashboard(user):
    """
    Return organization-level metrics for a Company Admin.
    """

    context = get_user_context(user)

    if context["role"] not in (
        UserRole.COMPANY_ADMIN,
        UserRole.SUPER_ADMIN,
    ):
        raise PermissionError(
            "Company Admin dashboard access is required."
        )

    org_filter = get_organization_filter(user)

    financial = get_financial_summary(user)

    return {
        "total_customers": Customer.objects.filter(
            **org_filter
        ).count(),

        "new_inquiries": Inquiry.objects.filter(
            status=InquiryStatus.NEW,
            **org_filter,
        ).count(),

        "active_bookings": Booking.objects.filter(
            status__in=get_active_booking_statuses(),
            **org_filter,
        ).count(),

        "upcoming_bookings": get_upcoming_booking_queryset(
            user
        ).count(),

        **financial,
    }
def get_finance_officer_dashboard(user):
    """
    Return financial metrics for a Finance Officer.
    """

    context = get_user_context(user)

    if context["role"] != UserRole.FINANCE_OFFICER:
        raise PermissionError(
            "Finance Officer dashboard access is required."
        )

    org_filter = get_organization_filter(user)

    total_invoices = Invoice.objects.filter(
        **org_filter
    ).count()

    paid_invoices = Invoice.objects.filter(
        status=InvoiceStatus.PAID,
        **org_filter,
    ).count()

    overdue_invoices = Invoice.objects.filter(
        status=InvoiceStatus.OVERDUE,
        **org_filter,
    ).count()

    total_invoiced = (
        Invoice.objects.filter(
            **org_filter
        ).aggregate(
            total=Sum("amount_due")
        )["total"]
        or 0
    )

    total_paid = (
        Payment.objects.filter(
            **org_filter
        ).aggregate(
            total=Sum("amount_paid")
        )["total"]
        or 0
    )

    return {
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue_invoices,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding_amount": total_invoiced - total_paid,
    }
def get_finance_officer_dashboard(user):
    """
    Return financial metrics for a Finance Officer.
    """

    context = get_user_context(user)

    if context["role"] != UserRole.FINANCE_OFFICER:
        raise PermissionError(
            "Finance Officer dashboard access is required."
        )

    org_filter = get_organization_filter(user)

    total_invoices = Invoice.objects.filter(
        **org_filter
    ).count()

    paid_invoices = Invoice.objects.filter(
        status=InvoiceStatus.PAID,
        **org_filter,
    ).count()

    overdue_invoices = Invoice.objects.filter(
        status=InvoiceStatus.OVERDUE,
        **org_filter,
    ).count()

    total_invoiced = (
        Invoice.objects.filter(
            **org_filter
        ).aggregate(
            total=Sum("amount_due")
        )["total"]
        or 0
    )

    total_paid = (
        Payment.objects.filter(
            **org_filter
        ).aggregate(
            total=Sum("amount_paid")
        )["total"]
        or 0
    )

    return {
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue_invoices,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding_amount": total_invoiced - total_paid,
    }
