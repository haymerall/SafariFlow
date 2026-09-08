# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet,
    GuideViewSet,
    SafariPackageViewSet,
    BookingViewSet,
    TourAssignmentViewSet,
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'guides', GuideViewSet, basename='guide')
router.register(r'packages', SafariPackageViewSet, basename='package')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'assignments', TourAssignmentViewSet, basename='assignment')

urlpatterns = [
    path('', include(router.urls)),
]
