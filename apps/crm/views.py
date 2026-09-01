from rest_framework import viewsets
from apps.core.mixins import OrganizationScopedMixin
from apps.core.permissions import IsOrganizationMember
from .models import Lead, Customer, Inquiry
from .serializers import LeadSerializer, CustomerSerializer, InquirySerializer


class LeadViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    """
    CRUD endpoints for Leads.
    Automatically scoped to the requesting user's organization.
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = (IsOrganizationMember,)
    filterset_fields = ('status',)
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('created_at', 'last_name')


class CustomerViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    """
    CRUD endpoints for Customers.
    Automatically scoped to the requesting user's organization.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsOrganizationMember,)
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('created_at', 'last_name')


class InquiryViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    """
    CRUD endpoints for Inquiries.
    Automatically scoped to the requesting user's organization.
    """
    queryset = Inquiry.objects.select_related('lead', 'customer').all()
    serializer_class = InquirySerializer
    permission_classes = (IsOrganizationMember,)
    filterset_fields = ('status',)
    ordering_fields = ('created_at', 'expected_travel_date')
