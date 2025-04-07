from django.http import JsonResponse
from .models import Session, AccuracyResult, PrivacyEvaluationResult, FairnessEvaluationResult
from django.core.management import call_command

def store_results(request):
    session = Session.objects.last()
    
    acc_with_dp = AccuracyResult.objects.filter(session=session, with_dp=True).first()
    acc_without_dp = AccuracyResult.objects.filter(session=session, with_dp=False).first()
    
    if not acc_with_dp or not acc_without_dp:
        call_command('store_results')  # Run the training command programmatically
        session = Session.objects.last()  # Refresh session
        acc_with_dp = AccuracyResult.objects.filter(session=session, with_dp=True).first()
        acc_without_dp = AccuracyResult.objects.filter(session=session, with_dp=False).first()

    privacy = PrivacyEvaluationResult.objects.filter(session=session, with_dp=True).first()
    fairness = FairnessEvaluationResult.objects.filter(session=session, with_dp=True).first()

    results = {
        "accuracy": {
            "with_dp": {
                "train": acc_with_dp.total_train_acc,
                "test": acc_with_dp.total_test_acc,
                "subgroups": {
                    "g0-": acc_with_dp.test_acc_g0_minus,
                    "g0+": acc_with_dp.test_acc_g0_plus,
                    "g1-": acc_with_dp.test_acc_g1_minus,
                    "g1+": acc_with_dp.test_acc_g1_plus,
                }
            },
            "without_dp": {
                "train": acc_without_dp.total_train_acc,
                "test": acc_without_dp.total_test_acc,
                "subgroups": {
                    "g0-": acc_without_dp.test_acc_g0_minus,
                    "g0+": acc_without_dp.test_acc_g0_plus,
                    "g1-": acc_without_dp.test_acc_g1_minus,
                    "g1+": acc_without_dp.test_acc_g1_plus,
                }
            },
        },
        "privacy": {
            "g0-": privacy.privacy_risk_g0_minus,
            "g0+": privacy.privacy_risk_g0_plus,
            "g1-": privacy.privacy_risk_g1_minus,
            "g1+": privacy.privacy_risk_g1_plus,
        },
        "fairness": {
            "bal_acc": fairness.bal_acc,
            "avg_odds_diff": fairness.avg_odds_diff,
            "disp_imp": fairness.disp_imp,
            "stat_par_diff": fairness.stat_par_diff,
            "eq_opp_diff": fairness.eq_opp_diff,
            "theil_ind": fairness.theil_ind,
        }
    }

    return JsonResponse(results)