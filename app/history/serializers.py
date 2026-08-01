from rest_framework import serializers

from data.models import Claim


class HistoryItemSerializer(serializers.ModelSerializer):
    verdict = serializers.CharField(source="final_result.verdict", read_only=True)
    credibility_score = serializers.FloatField(source="final_result.credibility_score", read_only=True)
    confidence_score = serializers.FloatField(source="final_result.confidence_score", read_only=True)
    explanation = serializers.CharField(source="final_result.llm_explanation", read_only=True)

    class Meta:
        model = Claim
        fields = (
            "id", "claim_text", "status", "verdict", "credibility_score",
            "confidence_score", "explanation", "created_at",
        )
