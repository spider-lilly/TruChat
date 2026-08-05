"""HTTP endpoints for the claim-processing service."""

import logging

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


from rest_framework.parsers import FormParser, JSONParser, MultiPartParser


class ClaimCheckRequestSerializer(serializers.Serializer):
    """Validate the payload accepted by the fact-checking endpoint."""

    claim_text = serializers.CharField(
        trim_whitespace=True,
        min_length=1,
        max_length=5_000,
        required=False,
    )


class ImageOCRView(APIView):
    """API endpoint to extract text from an uploaded image using OCR.space."""

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        image_input = (
            request.FILES.get("image")
            or request.FILES.get("file")
            or request.data.get("image")
            or request.data.get("image_input")
            or request.data.get("file")
            or request.data.get("base64")
        )

        if not image_input:
            return Response(
                {"detail": "No image file or image data provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_format = request.data.get("output_format", "markdown")

        try:
            from services.imgtotext import process_image

            result = process_image(image_input, output_format=output_format)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.warning("Invalid OCR input: %s", e)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TimeoutError as e:
            logger.error("OCR API timeout: %s", e)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            logger.exception("OCR processing failed: %s", e)
            return Response(
                {"detail": f"OCR extraction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClaimCheckView(APIView):
    """Run the fact-checking pipeline for one submitted claim or uploaded image."""

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        image_input = (
            request.FILES.get("image")
            or request.FILES.get("file")
            or request.data.get("image")
            or request.data.get("image_input")
        )

        if image_input:
            from services.imgtotext import process_image

            try:
                ocr_result = process_image(image_input)
                claim_text = ocr_result.get("formatted_text") or ocr_result.get("text", "")
            except ValueError as e:
                return Response(
                    {"detail": f"Invalid image input: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                logger.exception("OCR extraction failed during claim check.")
                return Response(
                    {"detail": f"Failed to extract text from image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            serializer = ClaimCheckRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            claim_text = serializer.validated_data.get("claim_text")

        if not claim_text:
            return Response(
                {"detail": "No text or image provided for claim checking."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from .pipeline import process_claim

            result = process_claim(
                claim_text,
                user=request.user if request.user.is_authenticated else None,
                input_source="OCR" if image_input else "TEXT",
            )
        except RuntimeError:
            logger.exception("Claim-processing pipeline failed.")
            return Response(
                {"detail": "The claim could not be processed."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            logger.exception("Unexpected claim-processing failure.")
            return Response(
                {"detail": "An unexpected error occurred while processing the claim."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "verdict": result.verdict,
                "credibility_score": result.credibility_score,
                "explanation": result.explanation,
            },
            status=status.HTTP_200_OK,
        )

