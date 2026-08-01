from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import Claim, ClaimStatus, Verdict

from .serializers import HistoryItemSerializer


class HistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        claims = Claim.objects.filter(user=request.user, status=ClaimStatus.COMPLETED).select_related("final_result").order_by("-created_at")
        return Response(HistoryItemSerializer(claims, many=True).data)


class HistoryCounterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        claims = Claim.objects.filter(user=request.user)
        verdict_counts = {
            item["final_result__verdict"]: item["count"]
            for item in claims.filter(status=ClaimStatus.COMPLETED).values("final_result__verdict").annotate(count=Count("id"))
        }
        return Response({
            "total": claims.count(),
            "completed": claims.filter(status=ClaimStatus.COMPLETED).count(),
            "processing": claims.filter(status=ClaimStatus.PROCESSING).count(),
            "failed": claims.filter(status=ClaimStatus.FAILED).count(),
            "supports": verdict_counts.get(Verdict.SUPPORTS, 0),
            "refutes": verdict_counts.get(Verdict.REFUTES, 0),
            "not_enough_information": verdict_counts.get(Verdict.NEI, 0),
        })

