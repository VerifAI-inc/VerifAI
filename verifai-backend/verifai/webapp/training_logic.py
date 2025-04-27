import os
import pandas as pd
import pickle
from ml_modules.training import train_orig, train_syn, train_rew, train_dir, train_eg
from ml_modules.model_loader import load_model
from ml_modules.data_loader import load_tabular_data
from ml_modules.summary import save_summary_tables
from .models import UploadedModel, UploadedDataset, AccuracyResult, FairnessEvaluationResult, PrivacyEvaluationResult

def run_full_training_pipeline(session):
    """
    Full pipeline: load data, model, run training, evaluate, and save results.
    """

    # 1. Load Uploaded Dataset and Model
    uploaded_model = UploadedModel.objects.get(session=session)
    uploaded_dataset = UploadedDataset.objects.get(session=session)

    model_path = uploaded_model.file.path
    dataset_path = uploaded_dataset.file.path

    # 2. Load Data
    dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute = load_tabular_data(
        dataset_path,
        uploaded_dataset.label_name,
        uploaded_dataset.pa_name,
        uploaded_dataset.fav_label,
        uploaded_dataset.priv_attb
    )

    # 3. Load Model
    # model_obj = pickle.load(open(model_path, "rb"))
    model_obj, original_model, dp_model_obj = load_model(model_path, session.epsilon, dataset_binary.features.shape[1])

    # 4. Determine mitigators
    mitigators = session.mitigators.split(",") if session.mitigators else []

    # 5. Run training depending on mitigators
    results = {}

    for mitigator in mitigators if mitigators else ["orig"]:
        if mitigator.lower() == "synthetic oversampling":
            train_func = train_syn
        elif mitigator.lower() == "rew":
            train_func = train_rew
        elif mitigator.lower() == "dir":
            train_func = train_dir
        elif mitigator.lower() == "eg":
            train_func = train_eg
        elif mitigator.lower() == "orig":
            train_func = train_orig
        else:
            continue  # Unknown mitigator, skip

        res = train_func(
            X=dataset_binary.features,
            y=dataset_binary.labels.ravel(),
            dataset_binary=dataset_binary,
            protected_attribute_index=protected_attribute_index,
            privileged_attribute=privileged_attribute,
            unprivileged_attribute=unprivileged_attribute,
            shadow_model_builder=lambda: original_model,
            target_model_builder=lambda: dp_model_obj,
            num_shadows=5
        )
        results[mitigator] = res

    # 6. Save results to database
    save_results_to_database(session, results)


def save_results_to_database(session, results):
    """
    Store Accuracy, Privacy, and Fairness metrics into the database.
    """

    for mitigator, res in results.items():
        # Save accuracy results
        AccuracyResult.objects.create(
            session=session,
            with_dp=False,  # Original without DP
            epsilon=session.epsilon,
            mitigator=mitigator,
            total_train_acc=sum(res['train_accuracies']) / len(res['train_accuracies']),
            total_test_acc=sum(res['test_accuracies']) / len(res['test_accuracies']),
            train_acc_g0_minus=res['subpop_train'][0].get("g0-", None),
            train_acc_g0_plus=res['subpop_train'][0].get("g0+", None),
            train_acc_g1_minus=res['subpop_train'][0].get("g1-", None),
            train_acc_g1_plus=res['subpop_train'][0].get("g1+", None),
            test_acc_g0_minus=res['subpop_test'][0].get("g0-", None),
            test_acc_g0_plus=res['subpop_test'][0].get("g0+", None),
            test_acc_g1_minus=res['subpop_test'][0].get("g1-", None),
            test_acc_g1_plus=res['subpop_test'][0].get("g1+", None),
        )

        # Save dummy privacy and fairness (later you can extend here with real ones)
        PrivacyEvaluationResult.objects.create(
            session=session,
            with_dp=False,
            epsilon=session.epsilon,
            mitigator=mitigator,
            privacy_risk_g0_minus=0.5,
            privacy_risk_g0_plus=0.5,
            privacy_risk_g1_minus=0.5,
            privacy_risk_g1_plus=0.5,
        )

        FairnessEvaluationResult.objects.create(
            session=session,
            with_dp=False,
            epsilon=session.epsilon,
            mitigator=mitigator,
            bal_acc=0.7,
            avg_odds_diff=0.1,
            disp_imp=1.2,
            stat_par_diff=0.05,
            eq_opp_diff=0.08,
            theil_ind=0.02,
        )
