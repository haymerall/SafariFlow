# pyrefly: ignore [missing-import]
from django.urls import path
from .views import MyOrganizationView

urlpatterns = [
    path('me/', MyOrganizationView.as_view(), name='organization-me'),
]
