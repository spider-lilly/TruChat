"""Database models for the claim credibility pipeline."""

import uuid

from django.conf import settings
from django.db import models
from pgvector.django import HnswIndex, VectorField

class ClaimStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class Verdict(models.TextChoices):
    SUPPORTS = "SUPPORTS", "Supports"
    REFUTES = "REFUTES", "Refutes"
    NEI = "NEI", "Not Enough Information"

class Claim(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="claims",
        null=True,
        blank=True,
    )
    claim_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    input_source = models.CharField(
        max_length=20,
        choices=(
            ("TEXT", "Text"),
            ("OCR", "OCR"),
        ),
        default="TEXT",
    )
    cleaned_claim = models.TextField(blank=True)
    normalized_claim = models.TextField(blank=True)
    canonical_claim = models.TextField(blank=True)

    fingerprint = models.TextField(blank=True)

    entities = models.JSONField(default=dict)

    keywords = models.JSONField(default=list)

    numbers = models.JSONField(default=list)

    dates = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        default=ClaimStatus.PENDING,
    )
    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.claim_text[:100]

class ClaimEmbedding(models.Model):

    claim = models.OneToOneField(
        Claim,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="embedding",
    )

    embedding_vector = VectorField(dimensions=1024)

    class Meta:
        indexes = [
            HnswIndex(
                name="claim_embedding_hnsw",
                fields=["embedding_vector"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="sources")
    url = models.URLField(max_length=2048)
    title = models.TextField(blank=True)
    source_name = models.CharField(max_length=512, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    raw_text = models.TextField(blank=True)
    cleaned_text = models.TextField(blank=True)
    source_reliability = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title or self.url


class SourceEmbedding(models.Model):
    # One embedding vector belongs to each source document.
    source = models.OneToOneField(
        Source,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="embedding",
    )
    embedding_vector = VectorField(dimensions=1024)


class NLIResult(models.Model):
    # The three NLI class probabilities for the source against its claim.
    source = models.OneToOneField(
        Source,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="nli_result",
    )
    supports = models.FloatField()
    contradicts = models.FloatField()
    neutral = models.FloatField()
    label = models.CharField(max_length=20)


class FinalResult(models.Model):
    # One final LLM assessment is retained for each claim.
    claim = models.OneToOneField(
        Claim,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="final_result",
    )
    verdict = models.CharField(
        max_length=20,
        choices=Verdict.choices,
    )
    confidence_score = models.FloatField(default=0.0)
    credibility_score = models.FloatField()
    llm_explanation = models.TextField()


class ExactClaimCache(models.Model):
    """Direct cache for a normalized claim and its completed evaluation."""

    normalized_claim = models.TextField(unique=True)
    verdict = models.CharField(max_length=20, choices=Verdict.choices)
    confidence_score = models.FloatField(default=0.0)
    credibility_score = models.FloatField()
    explanation = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
