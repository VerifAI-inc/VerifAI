from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "job_role", "created_at")
    search_fields = ("username", "email", "job_role")
    list_filter = ("job_role",)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("user", "dp_model_type", "epsilon", "created_at")
    search_fields = ("dp_model_type", "user__username")
    list_filter = ("epsilon",)

@admin.register(UploadedModel)
class UploadedModelAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "uploaded_at")
    search_fields = ("name", "user__username")
    list_filter = ("uploaded_at",)

@admin.register(UploadedDataset)
class UploadedDatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "uploaded_at")
    search_fields = ("name", "user__username")
    list_filter = ("uploaded_at",)

@admin.register(FairnessEvaluationResult)
class FairnessEvaluationResultAdmin(admin.ModelAdmin):
    list_display = ("session", "mitigator", "avg_odds_diff")
    search_fields = ("session__user__username", "mitigator")

@admin.register(PrivacyEvaluationResult)
class PrivacyEvaluationResultAdmin(admin.ModelAdmin):
    list_display = ("session", "with_dp", "privacy_risk_g0_minus")
    search_fields = ("session__user__username",)

@admin.register(AccuracyResult)
class AccuracyResultAdmin(admin.ModelAdmin):
    list_display = ("session", "mitigator", "total_test_acc")
    search_fields = ("session__user__username",)

@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ("session", "name", "creation_date")
    search_fields = ("session__user__username", "name")
    ordering = ("-creation_date",)