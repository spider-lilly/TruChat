from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from data.models import Claim, ClaimStatus, FinalResult, Verdict

from .views import HistoryCounterView, HistoryListView


User = get_user_model()


class HistoryApiTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="password123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="password123",
        )

        for index in range(21):
            claim = Claim.objects.create(
                user=self.user,
                claim_text=f"Claim {index}",
                status=ClaimStatus.COMPLETED,
                input_source="OCR" if index == 20 else "TEXT",
                normalized_claim=f"Normalized {index}",
                cleaned_claim=f"Cleaned {index}",
                canonical_claim=f"Canonical {index}",
                fingerprint=f"fingerprint-{index}",
            )
            FinalResult.objects.create(
                claim=claim,
                verdict=Verdict.SUPPORTS if index % 2 == 0 else Verdict.REFUTES,
                confidence_score=0.8,
                credibility_score=0.7,
                llm_explanation=f"Explanation {index}",
            )

        for index in range(3):
            claim = Claim.objects.create(
                user=self.other_user,
                claim_text=f"Other claim {index}",
                status=ClaimStatus.COMPLETED,
            )
            FinalResult.objects.create(
                claim=claim,
                verdict=Verdict.NEI,
                confidence_score=0.4,
                credibility_score=0.3,
                llm_explanation="Other explanation",
            )

    def test_history_list_is_paginated_and_scoped_to_user(self):
        request = self.factory.get("/api/history/?page=1")
        force_authenticate(request, user=self.user)

        response = HistoryListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 21)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertTrue(response.data["has_next"])
        self.assertEqual(response.data["next_page"], 2)
        self.assertTrue(response.data["results"][0]["is_ocr"])
        self.assertEqual(response.data["results"][0]["image_indicator"], "OCR")

    def test_history_counter_is_scoped_to_user(self):
        request = self.factory.get("/api/history/counter/")
        force_authenticate(request, user=self.user)

        response = HistoryCounterView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 21)
        self.assertEqual(response.data["completed"], 21)
        self.assertEqual(response.data["supports"], 11)
        self.assertEqual(response.data["refutes"], 10)
        self.assertEqual(response.data["not_enough_information"], 0)