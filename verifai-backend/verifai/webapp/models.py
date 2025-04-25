from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Custom User Model
class User(AbstractUser):
    job_role = models.CharField(max_length=255, blank=True, null=True)
    job_field = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    groups = models.ManyToManyField(Group, related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions")

# Session Table
class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dp_model_type = models.CharField(max_length=255)
    dp_model_parameters = models.JSONField()
    mitigators = models.CharField(max_length=255)
    epsilon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['user', 'epsilon'])] # Add index for performance

# Uploaded Model (ML Model)
class UploadedModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.OneToOneField(Session, on_delete=models.CASCADE) 
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="models/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Uploaded Dataset
class UploadedDataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    label_name = models.CharField(max_length=255)
    pa_name = models.CharField(max_length=255)
    fav_label = models.FloatField()
    priv_attb = models.FloatField()
    file = models.FileField(upload_to="datasets/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Fairness Evaluation Result (Updated Meta)
class FairnessEvaluationResult(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    with_dp = models.BooleanField()
    epsilon = models.FloatField()
    mitigator = models.CharField(max_length=255)
    bal_acc = models.FloatField(null=True, blank=True)
    avg_odds_diff = models.FloatField(null=True, blank=True)
    disp_imp = models.FloatField(null=True, blank=True)
    stat_par_diff = models.FloatField(null=True, blank=True)
    eq_opp_diff = models.FloatField(null=True, blank=True)
    theil_ind = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'with_dp', 'mitigator'], name='unique_fairness_session_withdp_mitigator')
        ]
        indexes = [models.Index(fields=['session', 'epsilon', 'with_dp', 'mitigator'])]

# Privacy Evaluation Result (Updated Meta)
class PrivacyEvaluationResult(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    with_dp = models.BooleanField()
    epsilon = models.FloatField()
    mitigator = models.CharField(max_length=255)
    privacy_risk_g0_minus = models.FloatField(null=True, blank=True)
    privacy_risk_g0_plus = models.FloatField(null=True, blank=True)
    privacy_risk_g1_minus = models.FloatField(null=True, blank=True)
    privacy_risk_g1_plus = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'with_dp', 'mitigator'], name='unique_privacy_session_withdp_mitigator')
        ]
        indexes = [models.Index(fields=['session', 'epsilon', 'with_dp', 'mitigator'])]

# Accuracy Results (Updated Meta)
class AccuracyResult(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    with_dp = models.BooleanField()
    epsilon = models.FloatField()
    mitigator = models.CharField(max_length=255)
    total_train_acc = models.FloatField(null=True, blank=True)
    total_test_acc = models.FloatField(null=True, blank=True)
    train_acc_g0_minus = models.FloatField(null=True, blank=True)
    train_acc_g0_plus = models.FloatField(null=True, blank=True)
    train_acc_g1_minus = models.FloatField(null=True, blank=True)
    train_acc_g1_plus = models.FloatField(null=True, blank=True)
    test_acc_g0_minus = models.FloatField(null=True, blank=True)
    test_acc_g0_plus = models.FloatField(null=True, blank=True)
    test_acc_g1_minus = models.FloatField(null=True, blank=True)
    test_acc_g1_plus = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'with_dp', 'mitigator'], name='unique_accuracy_session_withdp_mitigator')
        ]
        indexes = [models.Index(fields=['session', 'epsilon', 'with_dp', 'mitigator'])]

# Report History
class ReportHistory(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    content = models.TextField()