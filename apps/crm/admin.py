# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Lead, Customer, Inquiry

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status', 'organization', 'created_at')
    list_filter = ('status', 'organization', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-created_at',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'country', 'organization', 'created_at')
    list_filter = ('country', 'organization', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'destination_interest', 'expected_travel_date', 'organization', 'created_at')
    list_filter = ('status', 'organization', 'expected_travel_date')
    search_fields = ('destination_interest', 'lead__first_name', 'lead__last_name', 'customer__first_name', 'customer__last_name')
    ordering = ('-created_at',)
