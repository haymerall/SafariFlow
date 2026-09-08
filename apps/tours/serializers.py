# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Vehicle, Guide, SafariPackage, Booking, TourAssignment


def _related_org_id(obj):
    return getattr(obj, 'organization_id', None)


class SameOrganizationMixin:
    """Reject related objects that belong to another tenant."""

    def _request_org(self):
        request = self.context.get('request')
        if request is None or not getattr(request.user, 'is_authenticated', False):
            return None
        return request.user.organization

    def _ensure_same_org(self, attrs, field_names):
        org = self._request_org()
        if org is None:
            return
        errors = {}
        for name in field_names:
            obj = attrs.get(name, serializers.empty)
            if obj is serializers.empty:
                if self.instance is None:
                    continue
                obj = getattr(self.instance, name, None)
            if obj is None:
                continue
            if _related_org_id(obj) != org.id:
                errors[name] = 'Must belong to your organization.'
        if errors:
            raise serializers.ValidationError(errors)


class VehicleSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'registration_number', 'make', 'model', 'capacity',
            'status', 'status_display', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class GuideSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Guide
        fields = (
            'id', 'user', 'first_name', 'last_name', 'license_number',
            'languages_spoken', 'status', 'status_display',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_user(self, user):
        org = self.context['request'].user.organization
        if user is not None and org is not None and user.organization_id != org.id:
            raise serializers.ValidationError('Must belong to your organization.')
        return user


class SafariPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafariPackage
        fields = (
            'id', 'name', 'description', 'duration_days', 'base_price',
            'is_active', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class BookingSerializer(SameOrganizationMixin, serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer_name = serializers.SerializerMethodField()
    package_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id', 'customer', 'customer_name', 'inquiry', 'package', 'package_name',
            'start_date', 'end_date', 'total_passengers', 'status', 'status_display',
            'total_price', 'special_notes', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_customer_name(self, obj):
        return str(obj.customer) if obj.customer else None

    def get_package_name(self, obj):
        return str(obj.package) if obj.package else None

    def validate(self, attrs):
        self._ensure_same_org(attrs, ('customer', 'inquiry', 'package'))

        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {'end_date': 'Must be on or after start_date.'}
            )
        return attrs


class TourAssignmentSerializer(SameOrganizationMixin, serializers.ModelSerializer):
    class Meta:
        model = TourAssignment
        fields = (
            'id', 'booking', 'guide', 'vehicle', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        self._ensure_same_org(attrs, ('booking', 'guide', 'vehicle'))

        booking = attrs.get('booking', getattr(self.instance, 'booking', None))
        guide = attrs.get('guide', getattr(self.instance, 'guide', None))
        vehicle = attrs.get('vehicle', getattr(self.instance, 'vehicle', None))
        if booking is not None:
            booking_org = booking.organization_id
            errors = {}
            if guide is not None and guide.organization_id != booking_org:
                errors['guide'] = 'Must belong to the same organization as the booking.'
            if vehicle is not None and vehicle.organization_id != booking_org:
                errors['vehicle'] = 'Must belong to the same organization as the booking.'
            if errors:
                raise serializers.ValidationError(errors)
        return attrs
