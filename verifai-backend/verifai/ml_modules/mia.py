#IT IS NOT USED FOR NOW!
import numpy as np
from tensorflow_privacy.privacy.privacy_tests.membership_inference_attack import (
    advanced_mia as amia,
    membership_inference_attack as mia,
)
from tensorflow_privacy.privacy.privacy_tests.membership_inference_attack.data_structures import AttackInputData

def perform_mia(in_indices, stats, losses, num_shadows=5):
    """
    Perform LiRA membership inference attack.
    Returns AUC scores (list) and overall mean.
    """
    results = []
    for idx in range(num_shadows + 1):
        stat_target = stats[idx]
        in_indices_target = in_indices[idx]
        # Exclude target model from shadow models
        stat_shadow = np.array(stats[:idx] + stats[idx + 1:])
        in_indices_shadow = np.array(in_indices[:idx] + in_indices[idx + 1:])
        stat_in = [stat_shadow[:, j][in_indices_shadow[:, j]] for j in range(len(stat_target))]
        stat_out = [stat_shadow[:, j][~in_indices_shadow[:, j]] for j in range(len(stat_target))]
        scores = amia.compute_score_lira(stat_target, stat_in, stat_out, fix_variance=True)
        attack_input = AttackInputData(
            loss_train=scores[in_indices_target],
            loss_test=scores[~in_indices_target]
        )
        result_lira = mia.run_attacks(attack_input).single_attack_results[0]
        results.append(result_lira.get_auc())
    return np.round(results, 6), np.round(np.mean(results), 6)

def perform_mia_on_subgroups(X_combined, y_combined, protected_attr,
                             in_indices, stats, losses, num_shadows=5):
    """
    Perform membership inference attack on subgroups.
    Returns a dictionary with subgroup names and their mean AUC.
    """
    results_dict = {}
    if isinstance(X_combined, np.ndarray):
        subgroups = {
            'Privileged Favorable': ((X_combined[:, protected_attr] == 1) & (y_combined == 1)),
            'Unprivileged Favorable': ((X_combined[:, protected_attr] == 0) & (y_combined == 1)),
            'Unprivileged Unfavorable': ((X_combined[:, protected_attr] == 0) & (y_combined == 0)),
            'Privileged Unfavorable': ((X_combined[:, protected_attr] == 1) & (y_combined == 0)),
        }
    else:
        subgroups = {
            'Privileged Favorable': ((X_combined[protected_attr] == 1) & (y_combined == 1)),
            'Unprivileged Favorable': ((X_combined[protected_attr] == 0) & (y_combined == 1)),
            'Unprivileged Unfavorable': ((X_combined[protected_attr] == 0) & (y_combined == 0)),
            'Privileged Unfavorable': ((X_combined[protected_attr] == 1) & (y_combined == 0)),
        }
    for group_name, condition in subgroups.items():
        subgroup_indices = np.where(condition)[0]
        subgroup_in_indices = [arr[subgroup_indices] for arr in in_indices]
        subgroup_stat = [arr[subgroup_indices] for arr in stats]
        mia_results, mia_mean = perform_mia(subgroup_in_indices, subgroup_stat, losses, num_shadows=num_shadows)
        results_dict[group_name] = mia_mean
    return results_dict
