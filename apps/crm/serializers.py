from rest_framework import serializers
from .models import Lead, Customer, Inquiry


class LeadSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Lead
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'status', 'status_display', 'notes', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'address', 'country', 'notes', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class InquirySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    lead_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = (
            'id', 'lead', 'lead_name', 'customer', 'customer_name',
            'status', 'status_display', 'destination_interest',
            'expected_travel_date', 'number_of_travelers',
            'estimated_budget', 'special_requirements',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_lead_name(self, obj):
        return str(obj.lead) if obj.lead else None

    def get_customer_name(self, obj):
        return str(obj.customer) if obj.customer else None
