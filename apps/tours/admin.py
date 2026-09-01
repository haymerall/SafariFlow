# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Vehicle, Guide, SafariPackage, Booking, TourAssignment


class TourAssignmentInline(admin.TabularInline):
    """Show tour assignments directly inside a Booking record."""
    model = TourAssignment
    extra = 1
    fields = ('guide', 'vehicle', 'notes')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'registration_number', 'capacity', 'status', 'organization')
    list_filter = ('status', 'organization')
    search_fields = ('registration_number', 'make', 'model')
    ordering = ('organization', 'make', 'model')


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'license_number', 'languages_spoken', 'status', 'organization')
    list_filter = ('status', 'organization')
    search_fields = ('first_name', 'last_name', 'license_number')
    ordering = ('organization', 'last_name', 'first_name')


@admin.register(SafariPackage)
class SafariPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'base_price', 'is_active', 'organization')
    list_filter = ('is_active', 'organization')
    search_fields = ('name',)
    ordering = ('organization', 'name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'start_date', 'end_date', 'total_passengers', 'status', 'total_price', 'organization')
    list_filter = ('status', 'organization', 'start_date')
    search_fields = ('customer__first_name', 'customer__last_name')
    ordering = ('-start_date',)
    inlines = [TourAssignmentInline]


@admin.register(TourAssignment)
class TourAssignmentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'guide', 'vehicle')
    list_filter = ('guide', 'vehicle')
    search_fields = ('booking__customer__first_name', 'guide__first_name', 'vehicle__registration_number')
