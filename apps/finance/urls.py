# pyrefly: ignore [missing-import]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    InvoiceViewSet,
    PaymentViewSet,
    DocumentViewSet,
)


router = DefaultRouter()

router.register(
    'invoices',
    InvoiceViewSet,
    basename='invoice'
)

router.register(
    'payments',
    PaymentViewSet,
    basename='payment'
)

router.register(
    'documents',
    DocumentViewSet,
    basename='document'
)


urlpatterns = [
    path('', include(router.urls)),
]
