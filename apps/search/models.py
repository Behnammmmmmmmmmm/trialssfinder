"""Database models."""
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class SearchIndex(models.Model):
    """Simple search index for trials"""

    content_type: models.CharField = models.CharField(max_length=50)
    object_id: models.PositiveIntegerField = models.PositiveIntegerField()
    title: models.CharField = models.CharField(max_length=255)
    content: models.TextField = models.TextField()
    search_vector = SearchVectorField(null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content_type} - {self.title}"

    class Meta:
        db_table = "search_index"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            GinIndex(fields=["search_vector"]),
        ]
        unique_together = ["content_type", "object_id"]
