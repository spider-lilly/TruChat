# Generated to align the database schema with the claim-processing models.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Embedding",
            new_name="SourceEmbedding",
        ),
        migrations.AddField(
            model_name="claim",
            name="canonical_claim",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="claim",
            name="cleaned_claim",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="claim",
            name="dates",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="claim",
            name="entities",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="claim",
            name="fingerprint",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="claim",
            name="keywords",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="claim",
            name="numbers",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="claim",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PROCESSING", "Processing"),
                    ("COMPLETED", "Completed"),
                    ("FAILED", "Failed"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="claim",
            name="normalized_claim",
            field=models.TextField(blank=True),
        ),
        migrations.RenameField(
            model_name="source",
            old_name="publisher",
            new_name="source_name",
        ),
        migrations.AddField(
            model_name="finalresult",
            name="verdict",
            field=models.CharField(
                choices=[
                    ("SUPPORTS", "Supports"),
                    ("REFUTES", "Refutes"),
                    ("NEI", "Not Enough Information"),
                ],
                default="NEI",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="nliresult",
            name="label",
            field=models.CharField(default="NEI", max_length=20),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="ClaimEmbedding",
            fields=[
                (
                    "claim",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="embedding",
                        serialize=False,
                        to="data.claim",
                    ),
                ),
                ("embedding_vector", models.JSONField()),
            ],
        ),
    ]
