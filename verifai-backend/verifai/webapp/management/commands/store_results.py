from django.core.management.base import BaseCommand
from webapp.models import UploadedModel, UploadedDataset, Session, FairnessEvaluationResult, PrivacyEvaluationResult, AccuracyResult
from django.conf import settings
import os
import pickle
import pandas as pd
import math
from aif360.datasets import StandardDataset
from ml_modules.model_loader import load_model
from ml_modules.training import train_orig, train_dir, train_rew, train_syn, train_syn_target

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Helpers
def safe_get(d, key, default=0.0):
    try:
        val = d.get(key, default)
        if pd.isna(val) or val is None or (isinstance(val, float) and math.isnan(val)):
            return default
        return val
    except Exception:
        return default

class Command(BaseCommand):
    help = 'Run training and store evaluation results into database.'

    def handle(self, *args, **kwargs):
        session = Session.objects.last()
        dataset = UploadedDataset.objects.get(session=session)
        model = UploadedModel.objects.get(session=session)

        df = pd.read_csv(os.path.join(settings.MEDIA_ROOT, dataset.file.name))
        label_col = dataset.label_name
        protected_col = dataset.pa_name

        aif_dataset = StandardDataset(
            df,
            label_name=label_col,
            favorable_classes=[dataset.fav_label],
            protected_attribute_names=[protected_col],
            privileged_classes=[[dataset.priv_attb]]
        )

        X = aif_dataset.features
        y = aif_dataset.labels.ravel()
        prot_attr_idx = aif_dataset.feature_names.index(protected_col)

        model_path = os.path.join(settings.MEDIA_ROOT, model.file.name)
        num_features = X.shape[1]
        orig_model, original_model, dp_model = load_model(model_path, session.epsilon, num_features)

        subgroup_map = {
            "Unprivileged Unfavorable": "g0-",
            "Privileged Unfavorable": "g1-",
            "Unprivileged Favorable": "g0+",
            "Privileged Favorable": "g1+",
        }

        #### STEP 1: Always run Orig model first (no mitigator)
        for with_dp_flag in [False, True]:
            target_model = dp_model if with_dp_flag else original_model
            shadow_model_builder = lambda: original_model
            target_model_builder = lambda: target_model

            orig_results = train_orig(
                X, y, aif_dataset, prot_attr_idx, dataset.priv_attb, 1 - dataset.priv_attb,
                shadow_model_builder, target_model_builder
            )

            self.save_results(session, orig_results, with_dp_flag, mitigator="Orig", subgroup_map=subgroup_map)

        #### STEP 2: Then run user-chosen mitigator
        mitigator = session.mitigators

        if mitigator == "Reweighing":
            trainer = train_rew
        elif mitigator == "DIR":
            trainer = train_dir
        elif mitigator in ["Synthetic", "Sampling"]:
            trainer = train_syn
        else:
            trainer = train_orig  # fallback

        for with_dp_flag in [False, True]:
            target_model = dp_model if with_dp_flag else original_model
            shadow_model_builder = lambda: original_model
            target_model_builder = lambda: target_model

            results = trainer(
                X, y, aif_dataset, prot_attr_idx, dataset.priv_attb, 1 - dataset.priv_attb,
                shadow_model_builder, target_model_builder
            )

            self.save_results(session, results, with_dp_flag, mitigator=mitigator, subgroup_map=subgroup_map)

        self.stdout.write(self.style.SUCCESS("✅ Results stored successfully!"))

    def save_results(self, session, results, with_dp_flag, mitigator, subgroup_map):
        from webapp.models import AccuracyResult, FairnessEvaluationResult, PrivacyEvaluationResult

        subgroup_acc_test = {subgroup_map[k]: v for k, v in results['subpop_test'][-1].items() if k in subgroup_map}
        subgroup_acc_train = {subgroup_map[k]: v for k, v in results['subpop_train'][-1].items() if k in subgroup_map}
        subgroup_privacy = results.get('subgroup_means', {})
        metrics = results['all_metrics'][-1] if results['all_metrics'] else {}

        AccuracyResult.objects.update_or_create(
            session=session,
            with_dp=with_dp_flag,
            mitigator=mitigator,
            defaults={
                'epsilon': session.epsilon,
                'with_dp': with_dp_flag,
                'mitigator': mitigator,
                'total_train_acc': safe_get(results, 'train_accuracies'),
                'total_test_acc': safe_get(results, 'test_accuracies'),
                'train_acc_g0_minus': safe_get(subgroup_acc_train, "g0-"),
                'train_acc_g0_plus': safe_get(subgroup_acc_train, "g0+"),
                'train_acc_g1_minus': safe_get(subgroup_acc_train, "g1-"),
                'train_acc_g1_plus': safe_get(subgroup_acc_train, "g1+"),
                'test_acc_g0_minus': safe_get(subgroup_acc_test, "g0-"),
                'test_acc_g0_plus': safe_get(subgroup_acc_test, "g0+"),
                'test_acc_g1_minus': safe_get(subgroup_acc_test, "g1-"),
                'test_acc_g1_plus': safe_get(subgroup_acc_test, "g1+"),
            }
        )

        FairnessEvaluationResult.objects.update_or_create(
            session=session,
            with_dp=with_dp_flag,
            mitigator=mitigator,
            defaults={
                'epsilon': session.epsilon,
                'with_dp': with_dp_flag,
                'mitigator': mitigator,
                'bal_acc': safe_get(metrics, "balanced_accuracy"),
                'avg_odds_diff': safe_get(metrics, "average_odds_difference"),
                'disp_imp': safe_get(metrics, "disparate_impact"),
                'stat_par_diff': safe_get(metrics, "statistical_parity_difference"),
                'eq_opp_diff': safe_get(metrics, "equal_opportunity_difference"),
                'theil_ind': safe_get(metrics, "theil_index"),
            }
        )

        PrivacyEvaluationResult.objects.update_or_create(
            session=session,
            with_dp=with_dp_flag,
            mitigator=mitigator,
            defaults={
                'epsilon': session.epsilon,
                'with_dp': with_dp_flag,
                'mitigator': mitigator,
                'privacy_risk_g0_minus': safe_get(subgroup_privacy, "Unprivileged Unfavorable"),
                'privacy_risk_g0_plus': safe_get(subgroup_privacy, "Unprivileged Favorable"),
                'privacy_risk_g1_minus': safe_get(subgroup_privacy, "Privileged Unfavorable"),
                'privacy_risk_g1_plus': safe_get(subgroup_privacy, "Privileged Favorable"),
            }
        )