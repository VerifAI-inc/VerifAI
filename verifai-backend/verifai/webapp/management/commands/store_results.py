from django.core.management.base import BaseCommand
from webapp.models import UploadedModel, UploadedDataset, Session, FairnessEvaluationResult, PrivacyEvaluationResult, AccuracyResult
from django.conf import settings
import os
import pickle
import pandas as pd
from aif360.datasets import StandardDataset
from ml_modules.model_loader import load_model
from ml_modules.training import train_orig, train_dir, train_rew, train_syn, train_syn_target

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class Command(BaseCommand):
    help = 'Run training and store evaluation results into database.'

    def handle(self, *args, **kwargs):
        session = Session.objects.last()
        dataset = UploadedDataset.objects.get(session=session)
        model = UploadedModel.objects.get(session=session)

        # Load CSV dataset
        df = pd.read_csv(os.path.join(settings.MEDIA_ROOT, dataset.file.name))
        label_col = dataset.label_name
        protected_col = dataset.pa_name

        # Prepare AIF360 dataset
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

        # Load models
        model_path = os.path.join(settings.MEDIA_ROOT, model.file.name)
        num_features = X.shape[1]
        orig_model, original_model, dp_model = load_model(model_path, session.epsilon, num_features)

        shadow_model_builder = lambda: original_model
        target_model_builder = lambda: dp_model

        # Pick training function based on mitigator
        mitigator = session.mitigators
        if mitigator == "Reweighing":
            results = train_rew(X, y, aif_dataset, prot_attr_idx, dataset.priv_attb, 1 - dataset.priv_attb, shadow_model_builder, target_model_builder)
        elif mitigator == "DIR":
            results = train_dir(X, y, aif_dataset, prot_attr_idx, dataset.priv_attb, 1 - dataset.priv_attb, shadow_model_builder, target_model_builder)
        elif mitigator == "Synthetic" or mitigator == "Sampling":
            results = train_syn(X, y, aif_dataset, prot_attr_idx, dataset.priv_attb, 1 - dataset.priv_attb, shadow_model_builder, target_model_builder)
        else:
            results = train_orig(X, y, aif_dataset, prot_attr_idx, dataset.priv_attb, 1 - dataset.priv_attb, shadow_model_builder, target_model_builder)

        subgroup_map = {
            "Unprivileged Unfavorable": "g0-",
            "Privileged Unfavorable": "g1-",
            "Unprivileged Favorable": "g0+",
            "Privileged Favorable": "g1+",
        }

        subgroup_acc_test = {subgroup_map[k]: v for k, v in results['subpop_test'][-1].items() if k in subgroup_map}
        subgroup_acc_train = {subgroup_map[k]: v for k, v in results['subpop_train'][-1].items() if k in subgroup_map}

        # Save Accuracy Result
        AccuracyResult.objects.update_or_create(
            session=session,
            defaults={
                'epsilon': session.epsilon,
                'mitigator': mitigator,
                'total_train_acc': results['train_accuracies'][-1],
                'total_test_acc': results['test_accuracies'][-1],
                'train_acc_g0_minus': subgroup_acc_train.get("g0-"),
                'train_acc_g0_plus': subgroup_acc_train.get("g0+"),
                'train_acc_g1_minus': subgroup_acc_train.get("g1-"),
                'train_acc_g1_plus': subgroup_acc_train.get("g1+"),
                'test_acc_g0_minus': subgroup_acc_test.get("g0-"),
                'test_acc_g0_plus': subgroup_acc_test.get("g0+"),
                'test_acc_g1_minus': subgroup_acc_test.get("g1-"),
                'test_acc_g1_plus': subgroup_acc_test.get("g1+"),
            }
        )

        # Save Privacy Result
        subgroup_privacy = results['subgroup_means']
        PrivacyEvaluationResult.objects.update_or_create(
            session=session,
            defaults={
                'epsilon': session.epsilon,
                'with_dp': True,
                'privacy_risk_g0_minus': subgroup_privacy.get("Unprivileged Unfavorable"),
                'privacy_risk_g0_plus': subgroup_privacy.get("Unprivileged Favorable"),
                'privacy_risk_g1_minus': subgroup_privacy.get("Privileged Unfavorable"),
                'privacy_risk_g1_plus': subgroup_privacy.get("Privileged Favorable"),
            }
        )

        # Save Fairness Result
        metrics = results['all_metrics'][-1] if results['all_metrics'] else {}
        FairnessEvaluationResult.objects.update_or_create(
            session=session,
            defaults={
                'epsilon': session.epsilon,
                'with_dp': True,
                'mitigator': mitigator,
                'bal_acc': metrics.get("bal_acc"),
                'avg_odds_diff': metrics.get("avg_odds_diff"),
                'disp_imp': metrics.get("disp_imp"),
                'stat_par_diff': metrics.get("stat_par_diff"),
                'eq_opp_diff': metrics.get("eq_opp_diff"),
                'theil_ind': metrics.get("theil_ind"),
            }
        )

        self.stdout.write(self.style.SUCCESS("✅ Results stored successfully!"))