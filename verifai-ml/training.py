import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from metrics import get_stat_and_loss_tabular, calculate_subpopulation_accuracies, get_metrics
from tensorflow_privacy.privacy.privacy_tests.membership_inference_attack import advanced_mia as amia, membership_inference_attack as mia
from tensorflow_privacy.privacy.privacy_tests.membership_inference_attack.data_structures import AttackInputData
from oversampling import synthetic
from fairlearn.reductions import EqualizedOdds

# Fairness-related Pre-/In-processing
from aif360.algorithms.preprocessing import DisparateImpactRemover, LFR, OptimPreproc, Reweighing
from fairlearn.reductions import EqualizedOdds, ExponentiatedGradient
from aif360.sklearn.inprocessing import ExponentiatedGradientReduction
from aif360.metrics import utils, BinaryLabelDatasetMetric


###############################################################################
# Training function for Original Data (Before DP transformation)
###############################################################################
def train_orig(X, y, dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute, num_shadows=5,
               shadow_model_builder, target_model_builder):

    if target_model_builder is None:
        raise ValueError("You must provide a target_model_builder function for the DP model.")
        
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []

    favorable_label = dataset_binary.favorable_label
    unfavorable_label = dataset_binary.unfavorable_label
    
    # Define subgroup conditions (for membership inference on subpopulations)
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == favorable_label)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == favorable_label)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == unfavorable_label)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == unfavorable_label)),
    }
    
    for target_idx in range(num_shadows + 1):
        in_indices_list = []
        stats = []
        losses = []
        for i in range(num_shadows + 1):
            indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
            in_indices_list.append(indices)
            train_indices = indices
            val_indices = ~indices
            
            # Split the dataset using AIF360's subset() method
            dataset_train = dataset_binary.subset(train_indices)
            dataset_val = dataset_binary.subset(val_indices)
            X_train, y_train = dataset_train.features, dataset_train.labels.ravel()
            X_val, y_val = dataset_val.features, dataset_val.labels.ravel()
            
            if i == target_idx:
                model = target_model_builder()
            else:
                model = shadow_model_builder()
            model.fit(X_train, y_train)
            
            # For the target model record performance metrics.
            if i == target_idx:
                pred_train = model.predict(X_train)
                pred_test = model.predict(X_val)
                train_accuracies.append(accuracy_score(y_train, pred_train))
                test_accuracies.append(accuracy_score(y_val, pred_test))
                met = get_metrics(X_val, y_val, pred_test, protected_attribute_index)
                all_metrics.append(met)
                subpop_train = calculate_subpopulation_accuracies(X_train, y_train, protected_attribute_index, model)
                subpop_test = calculate_subpopulation_accuracies(X_val, y_val, protected_attribute_index, model)
                subpop_train_list.append(subpop_train)
                subpop_test_list.append(subpop_test)
            
            stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
            stats.append(stat)
            losses.append(loss)
        
        # Compute overall MIA for the target model using shadow models.
        stat_target = stats[target_idx]
        in_indices_target = in_indices_list[target_idx]
        stat_shadow = np.array([stats[i] for i in range(num_shadows + 1) if i != target_idx])
        in_indices_shadow = np.array([in_indices_list[i] for i in range(num_shadows + 1) if i != target_idx])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(loss_train=scores[in_indices_target],
                                       loss_test=scores[~in_indices_target])
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        overall_results.append(result_lira.get_auc())
        
        # Compute subgroup MIA for each subgroup.
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices_list]
            subgroup_stat = [arr[subgroup_indices] for arr in stats]
            subgroup_stat_target = subgroup_stat[target_idx]
            subgroup_in_indices_target = subgroup_in_indices[target_idx]
            subgroup_stat_shadow = np.array([subgroup_stat[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_in_indices_shadow = np.array([subgroup_in_indices[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_stat_in = [subgroup_stat_shadow[:, j][subgroup_in_indices_shadow[:, j]] 
                                for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_stat_out = [subgroup_stat_shadow[:, j][~subgroup_in_indices_shadow[:, j]] 
                                 for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_scores = amia.compute_score_lira(subgroup_stat_target, subgroup_stat_in, subgroup_stat_out, fix_variance=True)
            subgroup_attack_input = AttackInputData(loss_train=subgroup_scores[subgroup_in_indices_target],
                                                     loss_test=subgroup_scores[~subgroup_in_indices_target])
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    
    overall_mean = np.round(np.mean(overall_results), 6)
    subgroup_means = {group: np.round(np.mean(vals), 6) for group, vals in subgroup_results.items()}
    
    return {
        'overall_results': overall_results,
        'overall_mean': overall_mean,
        'subgroup_results': subgroup_results,
        'subgroup_means': subgroup_means,
        'train_accuracies': train_accuracies,
        'test_accuracies': test_accuracies,
        'subpop_train': subpop_train_list,
        'subpop_test': subpop_test_list,
        'all_metrics': all_metrics
    }

###############################################################################
# Training function for DIR (Before DP transformation)
###############################################################################
def train_dir(X, y, dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute, num_shadows=5,
               shadow_model_builder, target_model_builder):

    if target_model_builder is None:
        raise ValueError("You must provide a target_model_builder function for the DP model.")
        
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []

    favorable_label = dataset_binary.favorable_label
    unfavorable_label = dataset_binary.unfavorable_label
    
    # Define subgroup conditions (for membership inference on subpopulations)
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == favorable_label)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == favorable_label)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == unfavorable_label)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == unfavorable_label)),
    }

    DIR = DisparateImpactRemover(repair_level=0.5, sensitive_attribute=protected_attribute_name)
    dataset_dir = DIR.fit_transform(dataset_binary)
    
    for target_idx in range(num_shadows + 1):
        in_indices_list = []
        stats = []
        losses = []
        for i in range(num_shadows + 1):
            indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
            in_indices_list.append(indices)
            train_indices = indices
            val_indices = ~indices
            
            # Split the dataset using AIF360's subset() method
            dataset_train = dataset_dir.subset(train_indices)
            dataset_val = dataset_dir.subset(val_indices)
            X_train, y_train = dataset_train.features, dataset_train.labels.ravel()
            X_val, y_val = dataset_val.features, dataset_val.labels.ravel()
            
            if i == target_idx:
                model = target_model_builder()
            else:
                model = shadow_model_builder()
            model.fit(X_train, y_train)
            
            # For the target model record performance metrics.
            if i == target_idx:
                pred_train = model.predict(X_train)
                pred_test = model.predict(X_val)
                train_accuracies.append(accuracy_score(y_train, pred_train))
                test_accuracies.append(accuracy_score(y_val, pred_test))
                met = get_metrics(X_val, y_val, pred_test, protected_attribute_index)
                all_metrics.append(met)
                subpop_train = calculate_subpopulation_accuracies(X_train, y_train, protected_attribute_index, model)
                subpop_test = calculate_subpopulation_accuracies(X_val, y_val, protected_attribute_index, model)
                subpop_train_list.append(subpop_train)
                subpop_test_list.append(subpop_test)
            
            stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
            stats.append(stat)
            losses.append(loss)
        
        # Compute overall MIA for the target model using shadow models.
        stat_target = stats[target_idx]
        in_indices_target = in_indices_list[target_idx]
        stat_shadow = np.array([stats[i] for i in range(num_shadows + 1) if i != target_idx])
        in_indices_shadow = np.array([in_indices_list[i] for i in range(num_shadows + 1) if i != target_idx])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(loss_train=scores[in_indices_target],
                                       loss_test=scores[~in_indices_target])
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        overall_results.append(result_lira.get_auc())
        
        # Compute subgroup MIA for each subgroup.
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices_list]
            subgroup_stat = [arr[subgroup_indices] for arr in stats]
            subgroup_stat_target = subgroup_stat[target_idx]
            subgroup_in_indices_target = subgroup_in_indices[target_idx]
            subgroup_stat_shadow = np.array([subgroup_stat[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_in_indices_shadow = np.array([subgroup_in_indices[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_stat_in = [subgroup_stat_shadow[:, j][subgroup_in_indices_shadow[:, j]] 
                                for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_stat_out = [subgroup_stat_shadow[:, j][~subgroup_in_indices_shadow[:, j]] 
                                 for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_scores = amia.compute_score_lira(subgroup_stat_target, subgroup_stat_in, subgroup_stat_out, fix_variance=True)
            subgroup_attack_input = AttackInputData(loss_train=subgroup_scores[subgroup_in_indices_target],
                                                     loss_test=subgroup_scores[~subgroup_in_indices_target])
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    
    overall_mean = np.round(np.mean(overall_results), 6)
    subgroup_means = {group: np.round(np.mean(vals), 6) for group, vals in subgroup_results.items()}
    
    return {
        'overall_results': overall_results,
        'overall_mean': overall_mean,
        'subgroup_results': subgroup_results,
        'subgroup_means': subgroup_means,
        'train_accuracies': train_accuracies,
        'test_accuracies': test_accuracies,
        'subpop_train': subpop_train_list,
        'subpop_test': subpop_test_list,
        'all_metrics': all_metrics
    }


###############################################################################
# Training function with Synthetic Oversampling (After DP transformation)
###############################################################################
def train_syn(X, y, dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute, 
            num_shadows=5, shadow_model_builder, target_model_builder):
    """
    Train models using a synthetic oversampling transformation on the training data.
    This function requires additional parameters for the synthetic transformation.
    
    Returns a dictionary with overall and subgroup results, accuracies and metrics.
    """
    if target_model_builder is None:
        raise ValueError("You must provide a target_model_builder function for the DP model.")
   
    
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []

    favorable_label = dataset_binary.favorable_label
    unfavorable_label = dataset_binary.unfavorable_label

    protected_attribute_name = dataset_binary.feature_names[protected_attribute_index]

    privileged_groups = [{protected_attribute_name: privileged_attribute}]
    unprivileged_groups = [{protected_attribute_name: privileged_attribute}]
    
    metric_orig = BinaryLabelDatasetMetric(dataset_binary,
                                             unprivileged_groups=unprivileged_groups,
                                             privileged_groups=privileged_groups)
    
    base_rate_privileged_private = metric_orig.base_rate(privileged=True)
    base_rate_unprivileged_private = metric_orig.base_rate(privileged=False)

    
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == favorable_label)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == favorable_label)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == unfavorable_label)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == unfavorable_label)),
    }

    
    
    for target_idx in range(num_shadows + 1):
        in_indices_list = []
        stats = []
        losses = []
        for i in range(num_shadows + 1):
            indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
            in_indices_list.append(indices)
            train_indices = indices
            val_indices = ~indices
            
            dataset_train = dataset_binary.subset(train_indices)
            dataset_val = dataset_binary.subset(val_indices)
            transformed_dataset = synthetic(dataset_train,
                                            unprivileged_groups,
                                            base_rate_privileged_private,
                                            base_rate_unprivileged_private,
                                            favorable_label, unfavorable_label, os_mode=2)
            X_train, y_train = transformed_dataset.features, transformed_dataset.labels.ravel()
            X_val, y_val = dataset_val.features, dataset_val.labels.ravel()
            
            if i == target_idx:
                model = target_model_builder()
            else:
                model = shadow_model_builder()

            model.fit(X_train, y_train)
            
            if i == target_idx:
                pred_train = model.predict(X_train)
                pred_test = model.predict(X_val)
                train_accuracies.append(accuracy_score(y_train, pred_train))
                test_accuracies.append(accuracy_score(y_val, pred_test))
                met = get_metrics(X_val, y_val, pred_test, protected_attribute_index)
                all_metrics.append(met)
                subpop_train = calculate_subpopulation_accuracies(X_train, y_train, protected_attribute_index, model)
                subpop_test = calculate_subpopulation_accuracies(X_val, y_val, protected_attribute_index, model)
                subpop_train_list.append(subpop_train)
                subpop_test_list.append(subpop_test)
            
            stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
            stats.append(stat)
            losses.append(loss)
        
        stat_target = stats[target_idx]
        in_indices_target = in_indices_list[target_idx]
        stat_shadow = np.array([stats[i] for i in range(num_shadows + 1) if i != target_idx])
        in_indices_shadow = np.array([in_indices_list[i] for i in range(num_shadows + 1) if i != target_idx])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(loss_train=scores[in_indices_target],
                                       loss_test=scores[~in_indices_target])
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        overall_results.append(result_lira.get_auc())
        
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices_list]
            subgroup_stat = [arr[subgroup_indices] for arr in stats]
            subgroup_stat_target = subgroup_stat[target_idx]
            subgroup_in_indices_target = subgroup_in_indices[target_idx]
            subgroup_stat_shadow = np.array([subgroup_stat[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_in_indices_shadow = np.array([subgroup_in_indices[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_stat_in = [subgroup_stat_shadow[:, j][subgroup_in_indices_shadow[:, j]] 
                                for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_stat_out = [subgroup_stat_shadow[:, j][~subgroup_in_indices_shadow[:, j]] 
                                 for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_scores = amia.compute_score_lira(subgroup_stat_target, subgroup_stat_in, subgroup_stat_out, fix_variance=True)
            subgroup_attack_input = AttackInputData(loss_train=subgroup_scores[subgroup_in_indices_target],
                                                     loss_test=subgroup_scores[~subgroup_in_indices_target])
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    
    overall_mean = np.round(np.mean(overall_results), 6)
    subgroup_means = {group: np.round(np.mean(vals), 6) for group, vals in subgroup_results.items()}
    
    return {
        'overall_results': overall_results,
        'overall_mean': overall_mean,
        'subgroup_results': subgroup_results,
        'subgroup_means': subgroup_means,
        'train_accuracies': train_accuracies,
        'test_accuracies': test_accuracies,
        'subpop_train': subpop_train_list,
        'subpop_test': subpop_test_list,
        'all_metrics': all_metrics
    }

###############################################################################
# Training function where the target model is DP and trained on untransformed data
# (Shadow models are trained with the original builder)
###############################################################################
def train_syn_target(X, y, dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute, 
            num_shadows=5, shadow_model_builder, target_model_builder):
    """
    Train models using a synthetic oversampling transformation on the training data.
    This function requires additional parameters for the synthetic transformation.
    
    Returns a dictionary with overall and subgroup results, accuracies and metrics.
    """
    if target_model_builder is None:
        raise ValueError("You must provide a target_model_builder function for the DP model.")
        
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []
    
    favorable_label = dataset_binary.favorable_label
    unfavorable_label = dataset_binary.unfavorable_label

    protected_attribute_name = dataset_binary.feature_names[protected_attribute_index]

    privileged_groups = [{protected_attribute_name: privileged_attribute}]
    unprivileged_groups = [{protected_attribute_name: privileged_attribute}]
    
    metric_orig = BinaryLabelDatasetMetric(dataset_binary,
                                             unprivileged_groups=unprivileged_groups,
                                             privileged_groups=privileged_groups)
    
    base_rate_privileged_private = metric_orig.base_rate(privileged=True)
    base_rate_unprivileged_private = metric_orig.base_rate(privileged=False)

    
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == favorable_label)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == favorable_label)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == unfavorable_label)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == unfavorable_label)),
    }
    
    for target_idx in range(num_shadows + 1):
        in_indices_list = []
        stats = []
        losses = []
        for i in range(num_shadows + 1):
            indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
            in_indices_list.append(indices)
            train_indices = indices
            val_indices = ~indices
            
            if i == target_idx:
                dataset_train = dataset_binary.subset(train_indices)
                dataset_val = dataset_binary.subset(val_indices)
                transformed_dataset = synthetic(dataset_train,
                                                unprivileged_groups,
                                                base_rate_privileged_private,
                                                base_rate_unprivileged_private,
                                                favorable_label, unfavorable_label, os_mode=2)
                X_train, y_train = transformed_dataset.features, transformed_dataset.labels.ravel()
                X_val, y_val = dataset_val.features, dataset_val.labels.ravel()
                model = target_model_builder()
            else:
                X_train, y_train = X[train_indices], y[train_indices]
                X_val, y_val = X[val_indices], y[val_indices]
                model = shadow_model_builder()
            model.fit(X_train, y_train)
            
            if i == target_idx:
                pred_train = model.predict(X_train)
                pred_test = model.predict(X_val)
                train_accuracies.append(accuracy_score(y_train, pred_train))
                test_accuracies.append(accuracy_score(y_val, pred_test))
                met = get_metrics(X_val, y_val, pred_test, protected_attribute_index)
                all_metrics.append(met)
                subpop_train = calculate_subpopulation_accuracies(X_train, y_train, protected_attribute_index, model)
                subpop_test = calculate_subpopulation_accuracies(X_val, y_val, protected_attribute_index, model)
                subpop_train_list.append(subpop_train)
                subpop_test_list.append(subpop_test)
            
            stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
            stats.append(stat)
            losses.append(loss)
        
        stat_target = stats[target_idx]
        in_indices_target = in_indices_list[target_idx]
        stat_shadow = np.array([stats[i] for i in range(num_shadows + 1) if i != target_idx])
        in_indices_shadow = np.array([in_indices_list[i] for i in range(num_shadows + 1) if i != target_idx])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(loss_train=scores[in_indices_target],
                                       loss_test=scores[~in_indices_target])
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        overall_results.append(result_lira.get_auc())
        
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices_list]
            subgroup_stat = [arr[subgroup_indices] for arr in stats]
            subgroup_stat_target = subgroup_stat[target_idx]
            subgroup_in_indices_target = subgroup_in_indices[target_idx]
            subgroup_stat_shadow = np.array([subgroup_stat[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_in_indices_shadow = np.array([subgroup_in_indices[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_stat_in = [subgroup_stat_shadow[:, j][subgroup_in_indices_shadow[:, j]] 
                                for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_stat_out = [subgroup_stat_shadow[:, j][~subgroup_in_indices_shadow[:, j]] 
                                 for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_scores = amia.compute_score_lira(subgroup_stat_target, subgroup_stat_in, subgroup_stat_out, fix_variance=True)
            subgroup_attack_input = AttackInputData(loss_train=subgroup_scores[subgroup_in_indices_target],
                                                     loss_test=subgroup_scores[~subgroup_in_indices_target])
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    
    overall_mean = np.round(np.mean(overall_results), 6)
    subgroup_means = {group: np.round(np.mean(vals), 6) for group, vals in subgroup_results.items()}
    
    return {
        'overall_results': overall_results,
        'overall_mean': overall_mean,
        'subgroup_results': subgroup_results,
        'subgroup_means': subgroup_means,
        'train_accuracies': train_accuracies,
        'test_accuracies': test_accuracies,
        'subpop_train': subpop_train_list,
        'subpop_test': subpop_test_list,
        'all_metrics': all_metrics
    }

###############################################################################
# Training function using Reweighing (a fairness pre-processing method)
###############################################################################
def train_rew(X, y, dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute, 
            num_shadows=5, shadow_model_builder, target_model_builder):

    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []

    favorable_label = dataset_binary.favorable_label
    unfavorable_label = dataset_binary.unfavorable_label

    protected_attribute_name = dataset_binary.feature_names[protected_attribute_index]

    privileged_groups = [{protected_attribute_name: privileged_attribute}]
    unprivileged_groups = [{protected_attribute_name: privileged_attribute}]
    
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == favorable_label)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == favorable_label)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == unprivileged_attribute) & (y == unfavorable_label)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == privileged_attribute) & (y == unfavorable_label)),
    }
    
    RW = Reweighing(unprivileged_groups=unprivileged_groups,
                    privileged_groups=privileged_groups)
    
    for target_idx in range(num_shadows + 1):
        in_indices_list = []
        stats = []
        losses = []
        for i in range(num_shadows + 1):
            indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
            in_indices_list.append(indices)
            train_indices = indices
            val_indices = ~indices
            if i == target_idx:
                dataset_train = dataset_binary.subset(train_indices)
                dataset_val = dataset_binary.subset(val_indices)
                reweighted_dataset = RW.fit_transform(dataset_train)
                X_train = reweighted_dataset.features
                y_train = reweighted_dataset.labels.ravel().astype(int)
                X_val = dataset_val.features
                y_val = dataset_val.labels.ravel().astype(int)
                model = target_model_builder()
                model.fit(X_train, y_train, sample_weight=reweighted_dataset.instance_weights)
            else:
                X_train, y_train = X[train_indices], y[train_indices]
                X_val, y_val = X[val_indices], y[val_indices]
                model = shadow_model_builder()
                model.fit(X_train, y_train)
            
            if i == target_idx:
                pred_train = model.predict(X_train)
                pred_test = model.predict(X_val)
                train_accuracies.append(accuracy_score(y_train, pred_train))
                test_accuracies.append(accuracy_score(y_val, pred_test))
                met = get_metrics(X_val, y_val, pred_test, protected_attribute_index)
                all_metrics.append(met)
                subpop_train = calculate_subpopulation_accuracies(X_train, y_train, protected_attribute_index, model)
                subpop_test = calculate_subpopulation_accuracies(X_val, y_val, protected_attribute_index, model)
                subpop_train_list.append(subpop_train)
                subpop_test_list.append(subpop_test)
            
            stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
            stats.append(stat)
            losses.append(loss)
        
        stat_target = stats[target_idx]
        in_indices_target = in_indices_list[target_idx]
        stat_shadow = np.array([stats[i] for i in range(num_shadows + 1) if i != target_idx])
        in_indices_shadow = np.array([in_indices_list[i] for i in range(num_shadows + 1) if i != target_idx])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(loss_train=scores[in_indices_target],
                                       loss_test=scores[~in_indices_target])
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        overall_results.append(result_lira.get_auc())
        
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices_list]
            subgroup_stat = [arr[subgroup_indices] for arr in stats]
            subgroup_stat_target = subgroup_stat[target_idx]
            subgroup_in_indices_target = subgroup_in_indices[target_idx]
            subgroup_stat_shadow = np.array([subgroup_stat[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_in_indices_shadow = np.array([subgroup_in_indices[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_stat_in = [subgroup_stat_shadow[:, j][subgroup_in_indices_shadow[:, j]] for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_stat_out = [subgroup_stat_shadow[:, j][~subgroup_in_indices_shadow[:, j]] for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_scores = amia.compute_score_lira(subgroup_stat_target, subgroup_stat_in, subgroup_stat_out, fix_variance=True)
            subgroup_attack_input = AttackInputData(loss_train=subgroup_scores[subgroup_in_indices_target],
                                                     loss_test=subgroup_scores[~subgroup_in_indices_target])
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    
    overall_mean = np.round(np.mean(overall_results), 6)
    subgroup_means = {group: np.round(np.mean(vals), 6) for group, vals in subgroup_results.items()}
    
    return {
        'overall_results': overall_results,
        'overall_mean': overall_mean,
        'subgroup_results': subgroup_results,
        'subgroup_means': subgroup_means,
        'train_accuracies': train_accuracies,
        'test_accuracies': test_accuracies,
        'subpop_train': subpop_train_list,
        'subpop_test': subpop_test_list,
        'all_metrics': all_metrics
    }

###############################################################################
# Training function using Inprocessing (Exponentiated Gradient Reduction)
###############################################################################
def train_eg(dataframe, dataset_binary, protected_attribute_index, privileged_attribute, unprivileged_attribute, 
            num_shadows=5, shadow_model_builder, target_model_builder):

    label_name = dataset_binary.label_names[0]
    X = dataframe.drop(columns=[label_name])
    y = np.array(dataframe[label_name]).astype(int)
        
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []

    favorable_label = dataset_binary.favorable_label
    unfavorable_label = dataset_binary.unfavorable_label

    protected_attribute_name = dataset_binary.feature_names[protected_attribute_index]
    
    # Define subgroup conditions using the column name from the DataFrame
    subgroups = {
        'Privileged Favorable': ((X[protected_attribute_name] == privileged_attribute) & (y == favorable_label)),
        'Unprivileged Favorable': ((X[protected_attribute_name] == unprivileged_attribute) & (y == favorable_label)),
        'Unprivileged Unfavorable': ((X[protected_attribute_name] == unprivileged_attribute) & (y == unfavorable_label)),
        'Privileged Unfavorable': ((X[protected_attribute_name] == privileged_attribute) & (y == unfavorable_label)),
    }
    
    for target_idx in range(num_shadows + 1):
        in_indices_list = []
        stats = []
        losses = []
        for i in range(num_shadows + 1):
            indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
            in_indices_list.append(indices)
            X_train, y_train = X.iloc[indices], y[indices]
            X_val, y_val = X.iloc[~indices], y[~indices]
            if i == target_idx:
                _model = target_model_builder()
                constraint = EqualizedOdds(difference_bound=0.001)
                model = ExponentiatedGradientReduction(prot_attr=protected_attribute_name,
                                                       estimator=_model,
                                                       constraints=constraint)
                model.classes_ = np.unique(y)
                model.model_ = model.estimator
            else:
                model = shadow_model_builder()
            model.fit(X.iloc[indices], y[indices])
            
            if i == target_idx:
                pred_train = model.predict(X_train)
                pred_test = model.predict(X_val)
                train_accuracies.append(accuracy_score(y_train, pred_train))
                test_accuracies.append(accuracy_score(y_val, pred_test))
                met = get_metrics(X_val.to_numpy(), y_val, pred_test, protected_attribute_index)
                all_metrics.append(met)
                subpop_train = calculate_subpopulation_accuracies(X_train, y_train, protected_attribute_index, model)
                subpop_test = calculate_subpopulation_accuracies(X_val, y_val, protected_attribute_index, model)
                subpop_train_list.append(subpop_train)
                subpop_test_list.append(subpop_test)
            
            stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
            stats.append(stat)
            losses.append(loss)
        
        stat_target = stats[target_idx]
        in_indices_target = in_indices_list[target_idx]
        stat_shadow = np.array([stats[i] for i in range(num_shadows + 1) if i != target_idx])
        in_indices_shadow = np.array([in_indices_list[i] for i in range(num_shadows + 1) if i != target_idx])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(loss_train=scores[in_indices_target],
                                       loss_test=scores[~in_indices_target])
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        overall_results.append(result_lira.get_auc())
        
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices_list]
            subgroup_stat = [arr[subgroup_indices] for arr in stats]
            subgroup_stat_target = subgroup_stat[target_idx]
            subgroup_in_indices_target = subgroup_in_indices[target_idx]
            subgroup_stat_shadow = np.array([subgroup_stat[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_in_indices_shadow = np.array([subgroup_in_indices[i] for i in range(num_shadows + 1) if i != target_idx])
            subgroup_stat_in = [subgroup_stat_shadow[:, j][subgroup_in_indices_shadow[:, j]] for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_stat_out = [subgroup_stat_shadow[:, j][~subgroup_in_indices_shadow[:, j]] for j in range(len(subgroup_stat_shadow[0]))]
            subgroup_scores = amia.compute_score_lira(subgroup_stat_target, subgroup_stat_in, subgroup_stat_out, fix_variance=True)
            subgroup_attack_input = AttackInputData(loss_train=subgroup_scores[subgroup_in_indices_target],
                                                     loss_test=subgroup_scores[~subgroup_in_indices_target])
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    
    overall_mean = np.round(np.mean(overall_results), 6)
    subgroup_means = {group: np.round(np.mean(vals), 6) for group, vals in subgroup_results.items()}
    
    return {
        'overall_results': overall_results,
        'overall_mean': overall_mean,
        'subgroup_results': subgroup_results,
        'subgroup_means': subgroup_means,
        'train_accuracies': train_accuracies,
        'test_accuracies': test_accuracies,
        'subpop_train': subpop_train_list,
        'subpop_test': subpop_test_list,
        'all_metrics': all_metrics
    }
