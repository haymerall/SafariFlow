# pyrefly: ignore [missing-import]
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.core.mixins import OrganizationScopedMixin
from apps.core.permissions import IsOrganizationMember
from .models import Vehicle, Guide, SafariPackage, Booking, TourAssignment
from .serializers import (
    VehicleSerializer,
    GuideSerializer,
    SafariPackageSerializer,
    BookingSerializer,
    TourAssignmentSerializer,
)


class VehicleViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = (IsOrganizationMember,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('registration_number', 'make', 'model')
    ordering_fields = ('make', 'model', 'created_at')


class GuideViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    permission_classes = (IsOrganizationMember,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'last_name', 'license_number')
    ordering_fields = ('last_name', 'first_name', 'created_at')


class SafariPackageViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    queryset = SafariPackage.objects.all()
    serializer_class = SafariPackageSerializer
    permission_classes = (IsOrganizationMember,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name', 'duration_days', 'created_at')


class BookingViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('customer', 'inquiry', 'package').all()
    serializer_class = BookingSerializer
    permission_classes = (IsOrganizationMember,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('customer__first_name', 'customer__last_name')
    ordering_fields = ('start_date', 'created_at', 'status')


class TourAssignmentViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    queryset = TourAssignment.objects.select_related('booking', 'guide', 'vehicle').all()
    serializer_class = TourAssignmentSerializer
    permission_classes = (IsOrganizationMember,)
    organization_filter = 'booking__organization'
    filter_backends = (OrderingFilter,)
    ordering_fields = ('created_at',)
