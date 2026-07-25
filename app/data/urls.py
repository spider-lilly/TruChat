"""URL routes for claim-processing endpoints."""

from django.urls import path

from .services.views import ClaimCheckView

urlpatterns = [
    path("claims/check/", ClaimCheckView.as_view(), name="claim-check"),
]
