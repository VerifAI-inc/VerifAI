from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Custom User Model
class User(AbstractUser):
    job_role = models.CharField(max_length=255, blank=True, null=True)
    job_field = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

# Session Table
class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    dp_model_type = models.CharField(max_length=255)
    dp_model_parameters = models.JSONField()
    mitigators = models.CharField(max_length=255)
    epsilon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['epsilon']),
            models.Index(fields=['user', 'created_at'])
        ]

# Uploaded Model
class UploadedModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="uploaded_models", db_index=True)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="models/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Uploaded Dataset
class UploadedDataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="uploaded_datasets", db_index=True)
    name = models.CharField(max_length=255)
    label_name = models.CharField(max_length=255)
    pa_name = models.CharField(max_length=255)
    fav_label = models.FloatField()
    priv_attb = models.FloatField()
    file = models.FileField(upload_to="datasets/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Fairness Evaluation Result
class FairnessEvaluationResult(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="fairness_result")
    with_dp = models.BooleanField()
    mitigator = models.CharField(max_length=255)
    avg_odds_diff = models.FloatField(null=True, blank=True)

# Privacy Evaluation Result
class PrivacyEvaluationResult(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="privacy_result")
    with_dp = models.BooleanField()
    privacy_risk_g0_minus = models.FloatField(null=True, blank=True)

# Accuracy Result
class AccuracyResult(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="accuracy_result")
    mitigator = models.CharField(max_length=255)
    total_test_acc = models.FloatField(null=True, blank=True)

# Report History
class ReportHistory(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="report_history")
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        ordering = ["-creation_date"]