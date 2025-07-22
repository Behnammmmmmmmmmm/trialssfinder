"""Database models."""
from django.db import models

from apps.authentication.models import User
from apps.companies.models import Company


class Industry(models.Model):
    name: models.CharField = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Meta:
    db_table = "industries"


class Trial(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    company: models.ForeignKey = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="trials")
    title: models.CharField = models.CharField(max_length=255, db_index=True)
    description: models.TextField = models.TextField()
    industry: models.ForeignKey = models.ForeignKey(Industry, on_delete=models.CASCADE, db_index=True)
    location: models.CharField = models.CharField(max_length=255)
    start_date: models.DateField = models.DateField()
    end_date: models.DateField = models.DateField()
    status: models.CharField = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    is_featured: models.BooleanField = models.BooleanField(default=False, db_index=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def __str__(self):
        return self.title


class Meta:
    db_table = "trials"
    indexes = [
        models.Index(fields=["status", "-created_at"]),
    ]


class FavoriteTrial(models.Model):
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    trial: models.ForeignKey = models.ForeignKey(Trial, on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.trial.title}"


class Meta:
    db_table = "favorite_trials"
    unique_together = ["user", "trial"]


class UserIndustry(models.Model):
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    industry: models.ForeignKey = models.ForeignKey(Industry, on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.industry.name}"


class Meta:
    db_table = "user_industries"
    unique_together = ["user", "industry"]
