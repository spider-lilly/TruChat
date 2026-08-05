from django.db.models import Count
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import Claim, ClaimStatus, Verdict

from .serializers import HistoryItemSerializer


class HistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    page_size = 20

    def _parse_int(self, value, *, default=None, minimum=0):
        if value in (None, ""):
            return default

        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError({"detail": "Invalid pagination parameters."}) from exc

        if parsed < minimum:
            raise ValidationError({"detail": "Invalid pagination parameters."})

        return parsed

    def get(self, request):
        claims = (
            Claim.objects.filter(user=request.user, status=ClaimStatus.COMPLETED)
            .select_related("final_result")
            .order_by("-created_at", "-id")
        )

        total = claims.count()
        page = self._parse_int(request.query_params.get("page"), minimum=1)
        offset = self._parse_int(request.query_params.get("offset"), default=0, minimum=0)
        limit = self._parse_int(request.query_params.get("limit"), default=self.page_size, minimum=1)

        if page is not None:
            limit = self.page_size
            offset = (page - 1) * self.page_size
        else:
            limit = min(limit, self.page_size)

        if limit <= 0:
            limit = self.page_size

        current_page = page if page is not None else (offset // limit) + 1
        results = claims[offset:offset + limit]
        has_next = offset + limit < total

        return Response(
            {
                "results": HistoryItemSerializer(results, many=True).data,
                "has_next": has_next,
                "next_page": current_page + 1 if has_next else None,
                "total": total,
                "page": current_page,
                "page_size": limit,
                "offset": offset,
            }
        )


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

