from django.http import JsonResponse
from webapp.models import Session, FairnessEvaluationResult, PrivacyEvaluationResult, AccuracyResult

def store_results(request):
    session = Session.objects.last()  # or select based on user if needed

    # --- Privacy Results ---
    privacy_results = PrivacyEvaluationResult.objects.filter(session=session)

    privacy_data = {}
    for result in privacy_results:
        key = ""
        if result.mitigator.lower() == "orig" and not result.with_dp:
            key = "orig_without_dp"
        elif result.mitigator.lower() == "orig" and result.with_dp:
            key = "orig_with_dp"
        elif result.mitigator.lower() != "orig" and not result.with_dp:
            key = "mitigator_without_dp"
        elif result.mitigator.lower() != "orig" and result.with_dp:
            key = "mitigator_with_dp"

        privacy_data[key] = {
            "g0-": result.privacy_risk_g0_minus,
            "g0+": result.privacy_risk_g0_plus,
            "g1-": result.privacy_risk_g1_minus,
            "g1+": result.privacy_risk_g1_plus,
        }

    # --- Accuracy Results ---
    accuracy_results = AccuracyResult.objects.filter(session=session)

    accuracy_data = {}
    for result in accuracy_results:
        key = "with_dp" if result.with_dp else "without_dp"
        accuracy_data[key] = {
            "train": result.total_train_acc,
            "test": result.total_test_acc,
            "subgroups": {
                "g0-": result.test_acc_g0_minus,
                "g0+": result.test_acc_g0_plus,
                "g1-": result.test_acc_g1_minus,
                "g1+": result.test_acc_g1_plus,
            }
        }

    # --- Fairness Results ---
    fairness_result = FairnessEvaluationResult.objects.filter(session=session).first()
    fairness_data = {}
    if fairness_result:
        fairness_data = {
            "bal_acc": fairness_result.bal_acc,
            "avg_odds_diff": fairness_result.avg_odds_diff,
            "disp_imp": fairness_result.disp_imp,
            "stat_par_diff": fairness_result.stat_par_diff,
            "eq_opp_diff": fairness_result.eq_opp_diff,
            "theil_ind": fairness_result.theil_ind,
        }

    response = {
        "privacy": privacy_data,
        "accuracy": accuracy_data,
        "fairness": fairness_data,
    }

    return JsonResponse(response)