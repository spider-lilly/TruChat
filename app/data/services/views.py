"""HTTP endpoints for the claim-processing service."""

import logging

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class ClaimCheckRequestSerializer(serializers.Serializer):
    """Validate the payload accepted by the fact-checking endpoint."""

    claim_text = serializers.CharField(
        trim_whitespace=True,
        min_length=1,
        max_length=5_000,
    )


class ClaimCheckView(APIView):
    """Run the fact-checking pipeline for one submitted claim."""

    def post(self, request):
        serializer = ClaimCheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            from .pipeline import process_claim

            result = process_claim(serializer.validated_data["claim_text"])
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
                "confidence_score": result.confidence_score,
                "credibility_score": result.credibility_score,
                "explanation": result.explanation,
            },
            status=status.HTTP_200_OK,
        )
