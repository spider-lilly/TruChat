"""URL routes for claim-processing endpoints."""

from django.urls import path

from .views import ClaimCheckView, ImageOCRView

urlpatterns = [
    path("claims/check/", ClaimCheckView.as_view(), name="claim-check"),
    path("ocr/process/", ImageOCRView.as_view(), name="ocr-process"),
    path("image/process/", ImageOCRView.as_view(), name="image-process"),
]

