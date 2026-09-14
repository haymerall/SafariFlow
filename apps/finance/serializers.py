from rest_framework import serializers

from .models import Invoice, Payment, Document


class InvoiceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    booking_reference = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = (
            'id',
            'booking',
            'booking_reference',
            'invoice_number',
            'issue_date',
            'due_date',
            'amount_due',
            'currency',
            'status',
            'status_display',
            'notes',
            'amount_paid',
            'balance_due',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'invoice_number',
            'issue_date',
            'amount_paid',
            'balance_due',
            'created_at',
            'updated_at',
        )

    def get_booking_reference(self, obj):
        return str(obj.booking) if obj.booking else None

    def validate_booking(self, booking):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if (
            user
            and user.is_authenticated
            and user.organization is not None
            and booking.organization_id != user.organization_id
        ):
            raise serializers.ValidationError(
                'Must belong to your organization.'
            )

        return booking

    def validate(self, attrs):
        amount_due = attrs.get(
            'amount_due',
            getattr(self.instance, 'amount_due', None),
        )

        if amount_due is not None and amount_due < 0:
            raise serializers.ValidationError(
                {'amount_due': 'Must be zero or greater.'}
            )

        due_date = attrs.get(
            'due_date',
            getattr(self.instance, 'due_date', None),
        )
        issue_date = getattr(
            self.instance,
            'issue_date',
            None,
        )

        if issue_date and due_date and due_date < issue_date:
            raise serializers.ValidationError(
                {'due_date': 'Cannot be earlier than the issue date.'}
            )

        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True,
    )
    invoice_number = serializers.CharField(
        source='invoice.invoice_number',
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = (
            'id',
            'invoice',
            'invoice_number',
            'payment_date',
            'amount_paid',
            'payment_method',
            'payment_method_display',
            'reference_number',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'invoice_number',
            'created_at',
            'updated_at',
        )

    def validate_invoice(self, invoice):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if (
            user
            and user.is_authenticated
            and user.organization is not None
            and invoice.organization_id != user.organization_id
        ):
            raise serializers.ValidationError(
                'Must belong to your organization.'
            )

        return invoice

    def validate(self, attrs):
        amount_paid = attrs.get(
            'amount_paid',
            getattr(self.instance, 'amount_paid', None),
        )

        if amount_paid is not None and amount_paid <= 0:
            raise serializers.ValidationError(
                {'amount_paid': 'Must be greater than zero.'}
            )

        return attrs


class DocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True,
    )

    class Meta:
        model = Document
        fields = (
            'id',
            'booking',
            'invoice',
            'document_type',
            'document_type_display',
            'title',
            'file',
            'uploaded_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        org = getattr(user, 'organization', None)

        if org is None:
            return attrs

        errors = {}

        booking = attrs.get(
            'booking',
            getattr(self.instance, 'booking', None),
        )
        invoice = attrs.get(
            'invoice',
            getattr(self.instance, 'invoice', None),
        )
        uploaded_by = attrs.get(
            'uploaded_by',
            getattr(self.instance, 'uploaded_by', None),
        )

        if booking is not None and booking.organization_id != org.id:
            errors['booking'] = 'Must belong to your organization.'

        if invoice is not None and invoice.organization_id != org.id:
            errors['invoice'] = 'Must belong to your organization.'

        if (
            uploaded_by is not None
            and uploaded_by.organization_id is not None
            and uploaded_by.organization_id != org.id
        ):
            errors['uploaded_by'] = 'Must belong to your organization.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
# pyrefly: ignore [missing-import]
from rest_framework import serializers

from .models import Invoice, Payment, Document


class SameOrganizationMixin:
    """
    Ensures related objects belong to the same organization
    as the authenticated user.
    """

    def _request_org(self):
        request = self.context.get('request')

        if request is None:
            return None

        if not getattr(request.user, 'is_authenticated', False):
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

            if getattr(obj, 'organization_id', None) != org.id:
                errors[name] = (
                    'Must belong to your organization.'
                )

        if errors:
            raise serializers.ValidationError(errors)


class InvoiceSerializer(SameOrganizationMixin, serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    booking_reference = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    amount_paid = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    balance_due = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Invoice

        fields = (
            'id',
            'booking',
            'booking_reference',
            'customer_name',
            'invoice_number',
            'issue_date',
            'due_date',
            'amount_due',
            'amount_paid',
            'balance_due',
            'currency',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'invoice_number',
            'issue_date',
            'amount_paid',
            'balance_due',
            'created_at',
            'updated_at',
        )

    def get_booking_reference(self, obj):
        return str(obj.booking)

    def get_customer_name(self, obj):
        if obj.booking and obj.booking.customer:
            return str(obj.booking.customer)

        return None

    def validate(self, attrs):
        self._ensure_same_org(attrs, ('booking',))

        amount_due = attrs.get(
            'amount_due',
            getattr(self.instance, 'amount_due', None)
        )

        if amount_due is not None and amount_due < 0:
            raise serializers.ValidationError({
                'amount_due': (
                    'Amount due cannot be negative.'
                )
            })

        return attrs


class PaymentSerializer(SameOrganizationMixin, serializers.ModelSerializer):
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    invoice_number = serializers.CharField(
        source='invoice.invoice_number',
        read_only=True
    )

    class Meta:
        model = Payment

        fields = (
            'id',
            'invoice',
            'invoice_number',
            'payment_date',
            'amount_paid',
            'payment_method',
            'payment_method_display',
            'reference_number',
            'notes',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'invoice_number',
            'created_at',
            'updated_at',
        )

    def validate(self, attrs):
        self._ensure_same_org(attrs, ('invoice',))

        amount_paid = attrs.get(
            'amount_paid',
            getattr(self.instance, 'amount_paid', None)
        )

        if amount_paid is not None and amount_paid <= 0:
            raise serializers.ValidationError({
                'amount_paid': (
                    'Payment amount must be greater than zero.'
                )
            })

        return attrs


class DocumentSerializer(SameOrganizationMixin, serializers.ModelSerializer):
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )

    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Document

        fields = (
            'id',
            'booking',
            'invoice',
            'document_type',
            'document_type_display',
            'title',
            'file',
            'uploaded_by',
            'uploaded_by_name',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'uploaded_by',
            'uploaded_by_name',
            'created_at',
            'updated_at',
        )

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return str(obj.uploaded_by)

        return None

    def validate(self, attrs):
        self._ensure_same_org(attrs, ('booking', 'invoice'))

        return attrs
