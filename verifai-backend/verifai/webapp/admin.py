from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(UploadedModel)
admin.site.register(UploadedDataset)
admin.site.register(Session)
admin.site.register(FairnessEvaluationResult)
admin.site.register(PrivacyEvaluationResult)
admin.site.register(AccuracyResult)
admin.site.register(ReportHistory)