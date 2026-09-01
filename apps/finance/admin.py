from django.contrib import admin
from .models import Invoice, Payment, Document


class PaymentInline(admin.TabularInline):
    """Show all payments directly inside an Invoice record."""
    model = Payment
    extra = 1
    fields = ('payment_date', 'amount_paid', 'payment_method', 'reference_number', 'notes')
    readonly_fields = ()


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'booking', 'amount_due', 'currency',
        'status', 'issue_date', 'due_date', 'organization'
    )
    list_filter = ('status', 'currency', 'organization', 'issue_date')
    search_fields = (
        'invoice_number',
        'booking__customer__first_name',
        'booking__customer__last_name',
    )
    ordering = ('-issue_date',)
    readonly_fields = ('invoice_number', 'issue_date', 'amount_paid', 'balance_due')
    inlines = [PaymentInline]

    def amount_paid(self, obj):
        return obj.amount_paid
    amount_paid.short_description = 'Amount Paid'

    def balance_due(self, obj):
        return obj.balance_due
    balance_due.short_description = 'Balance Due'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'invoice', 'payment_date', 'amount_paid',
        'payment_method', 'reference_number', 'organization'
    )
    list_filter = ('payment_method', 'organization', 'payment_date')
    search_fields = ('invoice__invoice_number', 'reference_number')
    ordering = ('-payment_date',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'document_type', 'booking', 'invoice',
        'uploaded_by', 'organization', 'created_at'
    )
    list_filter = ('document_type', 'organization', 'created_at')
    search_fields = ('title', 'booking__customer__first_name', 'invoice__invoice_number')
    ordering = ('-created_at',)
