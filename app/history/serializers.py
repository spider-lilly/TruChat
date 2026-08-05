from rest_framework import serializers

from data.models import Claim


class HistoryItemSerializer(serializers.ModelSerializer):
    verdict = serializers.SerializerMethodField()
    confidence_score = serializers.SerializerMethodField()
    credibility_score = serializers.SerializerMethodField()
    explanation = serializers.SerializerMethodField()
    is_ocr = serializers.SerializerMethodField()
    image_indicator = serializers.SerializerMethodField()

    def get_verdict(self, obj):
        final_result = getattr(obj, "final_result", None)
        return getattr(final_result, "verdict", None)

    def get_confidence_score(self, obj):
        final_result = getattr(obj, "final_result", None)
        return getattr(final_result, "confidence_score", None)

    def get_credibility_score(self, obj):
        final_result = getattr(obj, "final_result", None)
        return getattr(final_result, "credibility_score", None)

    def get_explanation(self, obj):
        final_result = getattr(obj, "final_result", None)
        return getattr(final_result, "llm_explanation", None)

    def get_is_ocr(self, obj):
        return obj.input_source == "OCR"

    def get_image_indicator(self, obj):
        return "OCR" if obj.input_source == "OCR" else None

    class Meta:
        model = Claim
        fields = (
            "id",
            "claim_text",
            "normalized_claim",
            "cleaned_claim",
            "canonical_claim",
            "fingerprint",
            "entities",
            "keywords",
            "numbers",
            "dates",
            "status",
            "input_source",
            "is_ocr",
            "image_indicator",
            "verdict",
            "confidence_score",
            "credibility_score",
            "explanation",
            "created_at",
        )
