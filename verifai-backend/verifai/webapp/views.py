from django.http import JsonResponse
from webapp.models import Session, FairnessEvaluationResult, PrivacyEvaluationResult, AccuracyResult

def store_results(request):
    session = Session.objects.last()  # or select based on user if needed

    epsilons = [0.0, 0.1, 1, 5, 10]  # ✅ INCLUDE 0.0!

    all_results = {}

    for epsilon in epsilons:
        # --- Privacy Results ---
        privacy_results = PrivacyEvaluationResult.objects.filter(session=session, epsilon=epsilon)

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
        accuracy_results = AccuracyResult.objects.filter(session=session, epsilon=epsilon)

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
        fairness_results = FairnessEvaluationResult.objects.filter(session=session, epsilon=epsilon)

        fairness_data = {}
        for result in fairness_results:
            key = ""
            if result.mitigator.lower() == "orig" and not result.with_dp:
                key = "orig_without_dp"
            elif result.mitigator.lower() == "orig" and result.with_dp:
                key = "orig_with_dp"
            elif result.mitigator.lower() != "orig" and not result.with_dp:
                key = "mitigator_without_dp"
            elif result.mitigator.lower() != "orig" and result.with_dp:
                key = "mitigator_with_dp"

            fairness_data[key] = {
                "bal_acc": result.bal_acc,
                "avg_odds_diff": result.avg_odds_diff,
                "disp_imp": result.disp_imp,
                "stat_par_diff": result.stat_par_diff,
                "eq_opp_diff": result.eq_opp_diff,
                "theil_ind": result.theil_ind,
            }

        # --- Collect everything for this epsilon ---
        all_results[str(epsilon)] = {
            "privacy": privacy_data,
            "accuracy": accuracy_data,
            "fairness": fairness_data,
        }

    return JsonResponse(all_results)