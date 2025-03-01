import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import ClassificationMetric
from utils import log_loss, calculate_statistic

def get_stat_and_loss_tabular(model, x, y, batch_size=256, use_proba: bool = True):
    """
    Compute statistics and losses.
    """
    if use_proba:
        prob = model.predict_proba(x)
    else:
        prob = model.predict(x, batch_size=batch_size)
        if prob.shape[1] > 1:
            from scipy import special
            prob = special.softmax(prob, axis=-1)
    losses = log_loss(y, prob)
    stats = calculate_statistic(prob, y)
    return np.expand_dims(stats, axis=1), np.expand_dims(losses, axis=1)

def calculate_subpopulation_accuracies(X_combined, y_combined, protected_attribute_index, model):
    results = {}
    if isinstance(X_combined, pd.DataFrame):
        prot_col = X_combined.columns[protected_attribute_index]
        subgroups = {
            'Privileged Favorable': ((X_combined[prot_col] == 1) & (y_combined == 1)),
            'Unprivileged Favorable': ((X_combined[prot_col] == 0) & (y_combined == 1)),
            'Unprivileged Unfavorable': ((X_combined[prot_col] == 0) & (y_combined == 0)),
            'Privileged Unfavorable': ((X_combined[prot_col] == 1) & (y_combined == 0)),
        }
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            X_subgroup = X_combined.iloc[subgroup_indices]
            y_subgroup = np.array(y_combined)[subgroup_indices]
            predictions = model.predict(X_subgroup)
            accuracy = accuracy_score(y_subgroup, predictions)
            results[group_name] = accuracy
    else:
        subgroups = {
            'Privileged Favorable': ((X_combined[:, protected_attribute_index] == 1) & (y_combined == 1)),
            'Unprivileged Favorable': ((X_combined[:, protected_attribute_index] == 0) & (y_combined == 1)),
            'Unprivileged Unfavorable': ((X_combined[:, protected_attribute_index] == 0) & (y_combined == 0)),
            'Privileged Unfavorable': ((X_combined[:, protected_attribute_index] == 1) & (y_combined == 0)),
        }
        for group_name, condition in subgroups.items():
            subgroup_indices = np.where(condition)[0]
            X_subgroup = X_combined[subgroup_indices]
            y_subgroup = y_combined[subgroup_indices]
            predictions = model.predict(X_subgroup)
            accuracy = accuracy_score(y_subgroup, predictions)
            results[group_name] = accuracy
    return results

def get_metrics(X_test, y_test, y_pred, protected_attribute_index):
    """
    Calculate fairness and performance metrics using AIF360's ClassificationMetric.
    """
    num_features = X_test.shape[1]
    feature_names = [f'feature_{i}' for i in range(num_features)]
    df_true = pd.DataFrame(X_test, columns=feature_names)
    df_true['label'] = y_test
    df_pred = pd.DataFrame(X_test, columns=feature_names)
    df_pred['label'] = y_pred

    dataset_true = BinaryLabelDataset(
        favorable_label=1,
        unfavorable_label=0,
        df=df_true,
        label_names=['label'],
        protected_attribute_names=[f'feature_{protected_attribute_index}']
    )
    dataset_pred = BinaryLabelDataset(
        favorable_label=1,
        unfavorable_label=0,
        df=df_pred,
        label_names=['label'],
        protected_attribute_names=[f'feature_{protected_attribute_index}']
    )

    classification_metric = ClassificationMetric(
        dataset_true,
        dataset_pred,
        unprivileged_groups=[{f'feature_{protected_attribute_index}': 0}],
        privileged_groups=[{f'feature_{protected_attribute_index}': 1}]
    )
    
    balanced_accuracy = (classification_metric.sensitivity() + classification_metric.specificity()) / 2
    metrics = {
        'balanced_accuracy': balanced_accuracy,
        'average_odds_difference': classification_metric.average_odds_difference(),
        'disparate_impact': (1 - min((classification_metric.disparate_impact()),
                                      1 / classification_metric.disparate_impact())),
        'statistical_parity_difference': classification_metric.statistical_parity_difference(),
        'equal_opportunity_difference': classification_metric.equal_opportunity_difference(),
        'theil_index': classification_metric.theil_index()
    }
    return metrics

def average_dicts(dict_list):
    """Given a list of dictionaries, return a Series with the average for each key."""
    return pd.DataFrame(dict_list).mean()
