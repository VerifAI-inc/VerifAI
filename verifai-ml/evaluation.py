import os
import sys
import gc
import random
import warnings
import numpy as np
import pandas as pd
from scipy import special
from typing import Optional

# Scikit-learn and AIF360
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from imblearn.over_sampling import ADASYN
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import ClassificationMetric

# TensorFlow and Privacy Tools
import tensorflow as tf
from tensorflow_privacy.privacy.privacy_tests.membership_inference_attack import advanced_mia as amia, membership_inference_attack as mia
from tensorflow_privacy.privacy.privacy_tests.membership_inference_attack.data_structures import AttackInputData

# Fairness-related Pre-/In-processing
from aif360.algorithms.preprocessing import DisparateImpactRemover, LFR, OptimPreproc, Reweighing
from fairlearn.reductions import EqualizedOdds
from aif360.sklearn.inprocessing import ExponentiatedGradientReduction
from sklearn.base import clone  # Used to clone the user-uploaded model

###############################################
# 1. Utility Functions (loss & statistic)
###############################################
def log_loss(labels: np.ndarray,
             pred: np.ndarray,
             sample_weight: Optional[np.ndarray] = None,
             from_logits: bool = False,
             small_value: float = 1e-8) -> np.ndarray:
    """
    Computes the per-example cross-entropy loss.
    """
    if labels.shape[0] != pred.shape[0]:
        raise ValueError('Mismatch between labels and predictions.')
    if sample_weight is None:
        sample_weight = 1.0
    else:
        if np.shape(sample_weight)[0] != np.shape(labels)[0]:
            raise ValueError('Sample weights and labels must have the same length.')

    if pred.size == pred.shape[0]:
        pred = pred.flatten()
        if from_logits:
            pred = special.expit(pred)
        indices_class0 = (labels == 0)
        prob_correct = np.copy(pred)
        prob_correct[indices_class0] = 1 - prob_correct[indices_class0]
        return -np.log(np.maximum(prob_correct, small_value)) * sample_weight

    if from_logits:
        pred = special.softmax(pred, axis=-1)
    return -np.log(np.maximum(pred[np.arange(labels.size), labels], small_value)) * sample_weight


def calculate_statistic(probabilities: np.ndarray,
                        labels: np.ndarray,
                        sample_weight: Optional[np.ndarray] = None,
                        convert_to_prob: bool = False) -> np.ndarray:
    """
    Calculates, for each example, the probability assigned to the true class.
    """
    if convert_to_prob:
        probabilities = special.softmax(probabilities, axis=-1)
    stat = probabilities[np.arange(labels.size), labels]
    if sample_weight is not None:
        stat *= sample_weight
    return stat

#####################################
# 2. Model Builders
#####################################
def simple_nn_reduced(input_dim):
    """Simplified 2-layer neural network (using Keras Sequential)."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(2)
    ])
    return model


def scikit_learn_model():
    """Returns a scikit-learn DecisionTreeClassifier with max_depth=10."""
    return DecisionTreeClassifier(max_depth=10)

##############################################
# 3. Statistics and Loss Extraction Functions
##############################################
def get_stat_and_loss_tabular(model, x, y, batch_size=256, use_proba: bool = True):
    """
    Compute statistics and losses.
      - If use_proba is True then we assume a scikit-learn model (using predict_proba).
      - Otherwise (e.g. for neural nets) we use model.predict with an optional softmax conversion.
    Returns:
      A tuple (stats, losses) where each is an array with shape (n_samples, 1).
    """
    if use_proba:
        prob = model.predict_proba(x)
    else:
        prob = model.predict(x, batch_size=batch_size)
        if prob.shape[1] > 1:
            prob = special.softmax(prob, axis=-1)
    losses = log_loss(y, prob)
    stats = calculate_statistic(prob, y)
    return np.expand_dims(stats, axis=1), np.expand_dims(losses, axis=1)

############################################
# 4. Accuracy & Metric Calculation Methods
############################################
def calculate_subpopulation_accuracies(X_combined, y_combined, protected_attribute_index, model):
    """
    Compute accuracy metrics for overall and each subgroup.
    Returns a dictionary mapping subgroup names to their accuracy.
    """
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
    Returns a dictionary of metrics.
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


def compute_mean_accuracies(accuracies_train, accuracies_test, train_subpop, test_subpop):
    """
    Compute mean overall and subpopulation accuracies.
    Returns a dictionary with these values.
    """
    mean_train_overall = np.mean(accuracies_train)
    mean_test_overall = np.mean(accuracies_test)
    mean_train_subpop = {key: np.mean([sub[key] for sub in train_subpop])
                         for key in train_subpop[0].keys()}
    mean_test_subpop = {key: np.mean([sub[key] for sub in test_subpop])
                        for key in test_subpop[0].keys()}
    return {
       "mean_train_overall": mean_train_overall,
       "mean_test_overall": mean_test_overall,
       "mean_train_subpop": mean_train_subpop,
       "mean_test_subpop": mean_test_subpop,
    }

##############################################
# 5. Membership Inference Attack Functions
##############################################
def perform_mia(in_indices, stats, losses, num_shadows=5):
    """
    For each model (treated as the target), use the other models as shadows to perform the LiRA attack.
    Returns a dictionary with:
      - 'individual_auc': a list of AUC scores for each model.
      - 'mean_auc': the overall mean AUC.
    """
    results = []
    for idx in range(num_shadows + 1):
        stat_target = stats[idx]
        in_indices_target = in_indices[idx]
        # Exclude the target model from the shadows:
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
    return {"individual_auc": np.round(results, 6).tolist(), "mean_auc": float(np.round(np.mean(results), 6))}


def perform_mia_on_subgroups(X_combined, y_combined, protected_attr,
                             in_indices, stats, losses, num_shadows=5):
    """
    Perform MIA for each subgroup.
    Returns a dictionary mapping subgroup names to their mean AUC.
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
        mia_result = perform_mia(subgroup_in_indices, subgroup_stat, [arr[subgroup_indices] for arr in losses], num_shadows=num_shadows)
        results_dict[group_name] = mia_result["mean_auc"]
    return results_dict

#####################################
# 6. Oversampling/Synthetic Methods
#####################################
def group_indices(dataset, unprivileged_groups):
    """
    Returns indices of examples in the unprivileged and privileged groups.
    """
    feature_names = dataset.feature_names
    from aif360.metrics import utils
    cond_vec = utils.compute_boolean_conditioning_vector(dataset.features, feature_names, unprivileged_groups)
    indices = [i for i, x in enumerate(cond_vec) if x]
    priv_indices = [i for i, x in enumerate(cond_vec) if not x]
    return indices, priv_indices


def balance(dataset, n_extra, inflate_rate, f_label, uf_label):
    """
    Oversample one group using ADASYN and then select extra samples.
    Returns a tuple: (dataset_transf_train, dataset_extra_train).
    """
    dataset_transf_train = dataset.copy(deepcopy=True)
    f_indices = np.where(dataset.labels == f_label)[0].tolist()
    uf_indices = np.where(dataset.labels == uf_label)[0].tolist()
    f_dataset = dataset.subset(f_indices)
    uf_dataset = dataset.subset(uf_indices)
    
    inflated_uf_features = np.repeat(uf_dataset.features, inflate_rate, axis=0)
    sample_features = np.concatenate((f_dataset.features, inflated_uf_features))
    inflated_uf_labels = np.repeat(uf_dataset.labels, inflate_rate, axis=0)
    sample_labels = np.concatenate((f_dataset.labels, inflated_uf_labels))
    
    oversample = ADASYN(sampling_strategy='minority')
    X, y = oversample.fit_resample(sample_features, sample_labels)
    y = y.reshape(-1, 1)
    # Only keep samples of f_label (favorable)
    X = X[np.where(y == f_label)[0].tolist()]
    y = y[y == f_label]
    selected = int(f_dataset.features.shape[0] + n_extra)
    X = X[:selected, :]
    y = y[:selected]
    y = y.reshape(-1, 1)
    
    instance_weights_list = (f_dataset.instance_weights.flatten().tolist()
                             if isinstance(f_dataset.instance_weights, np.ndarray)
                             else f_dataset.instance_weights)
    protected_attributes_list = (f_dataset.protected_attributes.flatten().tolist()
                                 if isinstance(f_dataset.protected_attributes, np.ndarray)
                                 else f_dataset.protected_attributes)
    inc = X.shape[0] - f_dataset.features.shape[0]
    new_weights = [random.choice(instance_weights_list) for _ in range(inc)]
    new_attributes = np.array([random.choice(protected_attributes_list) for _ in range(inc)]).reshape(-1, 1)
    
    dataset_transf_train.features = np.concatenate((uf_dataset.features, X))
    dataset_transf_train.labels = np.concatenate((uf_dataset.labels, y))
    dataset_transf_train.instance_weights = np.concatenate((uf_dataset.instance_weights, f_dataset.instance_weights, new_weights))
    dataset_transf_train.protected_attributes = np.concatenate((uf_dataset.protected_attributes, f_dataset.protected_attributes, new_attributes))
    
    dataset_extra_train = dataset.copy()
    X_ex = X[-int(n_extra):]
    y_ex = y[-int(n_extra):].reshape(-1, 1)
    new_weights = [random.choice(instance_weights_list) for _ in range(int(n_extra))]
    new_attributes = np.array([random.choice(protected_attributes_list) for _ in range(int(n_extra))]).reshape(-1, 1)
    dataset_extra_train.features = X_ex
    dataset_extra_train.labels = y_ex
    dataset_extra_train.instance_weights = new_weights
    dataset_extra_train.protected_attributes = new_attributes
    return dataset_transf_train, dataset_extra_train

def synthetic_balance(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0):
    """
    Oversample the unprivileged group so that the number of favorable samples matches that of the privileged group.
    Returns the transformed dataset.
    """
    dataset_transf_train = dataset.copy(deepcopy=True)
    indices, priv_indices = group_indices(dataset, unprivileged_groups)
    unprivileged_dataset = dataset.subset(indices)
    privileged_dataset = dataset.subset(priv_indices)
    n_unpriv_favor = np.count_nonzero(unprivileged_dataset.labels == f_label)
    n_unpriv_unfavor = np.count_nonzero(unprivileged_dataset.labels != f_label)
    n_priv_favor = np.count_nonzero(privileged_dataset.labels == f_label)
    
    if n_unpriv_favor < n_priv_favor:
        n_extra_sample = (n_priv_favor - n_unpriv_favor) * sampling_strategy
        if n_extra_sample + n_unpriv_favor >= n_unpriv_unfavor:
            inflate_rate = int(((n_extra_sample + n_unpriv_favor) / n_unpriv_unfavor) + 1)
        else:
            inflate_rate = round(((n_extra_sample + n_unpriv_favor) / n_unpriv_unfavor) + 1)
        _, extra_favored = balance(unprivileged_dataset, n_extra_sample, inflate_rate, f_label, uf_label)
        
        n_extra_sample = (n_extra_sample + n_unpriv_favor - bp * (n_extra_sample + n_unpriv_favor + n_unpriv_unfavor)) / bp
        if n_extra_sample + n_unpriv_unfavor >= n_unpriv_favor:
            inflate_rate = int(((n_extra_sample + n_unpriv_unfavor) / n_unpriv_favor) + 1)
        else:
            inflate_rate = round(((n_extra_sample + n_unpriv_unfavor) / n_unpriv_favor) + 1)
        _, extra_unfavored = balance(unprivileged_dataset, n_extra_sample, inflate_rate, uf_label, f_label)
        
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, extra_favored.features, extra_unfavored.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, extra_favored.labels, extra_unfavored.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, extra_favored.instance_weights, extra_unfavored.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, extra_favored.protected_attributes, extra_unfavored.protected_attributes))
    return dataset_transf_train

def synthetic_favor_unpriv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0):
    """
    Oversample favorable examples in the unprivileged group.
    Returns a tuple: (unprivileged_dataset, extra_favored_unpriv).
    """
    indices, priv_indices = group_indices(dataset, unprivileged_groups)
    unprivileged_dataset = dataset.subset(indices)
    privileged_dataset = dataset.subset(priv_indices)
    n_unpriv_favor = np.count_nonzero(unprivileged_dataset.labels == f_label)
    n_unpriv_unfavor = np.count_nonzero(unprivileged_dataset.labels != f_label)
    n_extra_sample = (bp * len(indices) - n_unpriv_favor) / (1 - bp) * sampling_strategy
    if n_extra_sample + n_unpriv_favor >= n_unpriv_unfavor:
        inflate_rate = int(((n_extra_sample + n_unpriv_favor) / n_unpriv_unfavor) + 1)
    else:
        inflate_rate = round(((n_extra_sample + n_unpriv_favor) / n_unpriv_unfavor) + 1)
    _, extra_favored_unpriv = balance(unprivileged_dataset, n_extra_sample, inflate_rate, f_label, uf_label)
    return unprivileged_dataset, extra_favored_unpriv

def synthetic_unfavor_priv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0):
    """
    Oversample the unfavored examples in the privileged group.
    Returns a tuple: (privileged_dataset, extra_unfavored_priv).
    """
    indices, priv_indices = group_indices(dataset, unprivileged_groups)
    unprivileged_dataset = dataset.subset(indices)
    privileged_dataset = dataset.subset(priv_indices)
    n_priv_favor = np.count_nonzero(privileged_dataset.labels == f_label)
    n_priv_unfavor = np.count_nonzero(privileged_dataset.labels != f_label)
    n_extra_sample = (n_priv_favor - bnp * len(priv_indices)) / bnp * sampling_strategy
    if n_extra_sample + n_priv_unfavor >= n_priv_favor:
        inflate_rate = int(((n_extra_sample + n_priv_unfavor) / n_priv_favor) + 1)
    else:
        inflate_rate = round(((n_extra_sample + n_priv_unfavor) / n_priv_favor) + 1)
    _, extra_unfavored_priv = balance(privileged_dataset, n_extra_sample, inflate_rate, uf_label, f_label)
    return privileged_dataset, extra_unfavored_priv

def synthetic(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, os_mode=2, sampling_strategy=0.5):
    """
    Depending on os_mode, perform one of the following oversampling methods:
      1: Oversample unfavorable privileged.
      2: Oversample favorable unprivileged.
      3: Both.
    If bp < bnp then use synthetic_balance.
    Returns the transformed dataset.
    """
    dataset_transf_train = dataset.copy(deepcopy=True)
    if bp < bnp:
        dataset_transf_train = synthetic_balance(dataset, unprivileged_groups, bp, bnp, f_label, uf_label)
        return dataset_transf_train

    if os_mode == 1:
        _, sample_unfavor_priv = synthetic_unfavor_priv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_unfavor_priv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_unfavor_priv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_unfavor_priv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_unfavor_priv.protected_attributes))
    elif os_mode == 2:
        _, sample_favor_unpriv = synthetic_favor_unpriv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_favor_unpriv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_favor_unpriv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_favor_unpriv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_favor_unpriv.protected_attributes))
    elif os_mode == 3:
        _, sample_unfavor_priv = synthetic_unfavor_priv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_unfavor_priv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_unfavor_priv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_unfavor_priv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_unfavor_priv.protected_attributes))
        _, sample_favor_unpriv = synthetic_favor_unpriv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy=1.0)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_favor_unpriv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_favor_unpriv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_favor_unpriv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_favor_unpriv.protected_attributes))
    else:
        sys.exit("Oversampling mode is missing: 1, 2, or 3 must be specified.")
    return dataset_transf_train

##############################################
# 7. Training Functions for Different Scenarios
##############################################
def train_shadow_model(X, y, indices, protected_attribute_index, model_builder=scikit_learn_model):
    """
    Train one model on X[indices] and compute predictions, metrics, subpopulation accuracies,
    and obtain the per-example statistics and losses.
    Returns a dictionary with results.
    """
    model = model_builder()
    model.fit(X[indices], y[indices])
    pred_train = model.predict(X[indices])
    pred_test = model.predict(X[~indices])
    metrics = get_metrics(X[~indices], y[~indices], pred_test, protected_attribute_index)
    acc_train = accuracy_score(y[indices], pred_train)
    acc_test = accuracy_score(y[~indices], pred_test)
    subpop_train = calculate_subpopulation_accuracies(X[indices], y[indices], protected_attribute_index, model)
    subpop_test = calculate_subpopulation_accuracies(X[~indices], y[~indices], protected_attribute_index, model)
    stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
    return {
        'model': model,
        'accuracy_train': acc_train,
        'accuracy_test': acc_test,
        'metrics': metrics,
        'subpop_train': subpop_train,
        'subpop_test': subpop_test,
        'stat': stat,
        'loss': loss
    }

def train_models(X, y, protected_attribute_index, num_shadows=5, model_builder=scikit_learn_model, user_model=None):
    """
    Train a collection of models on the data arrays.
    If a user_model is provided, it is used for every iteration (both target and shadow) by cloning it.
    Returns a dictionary with lists for in_indices, stats, losses, subpopulation accuracies, and overall accuracies.
    """
    n_samples = X.shape[0]
    in_indices_list = []
    stats = []
    losses = []
    accuracies_train = []
    accuracies_test = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []
    
    for i in range(num_shadows + 1):
        indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
        in_indices_list.append(indices)
        if user_model is not None:
            model = clone(user_model)
            model.fit(X[indices], y[indices])
        else:
            model = model_builder()
            model.fit(X[indices], y[indices])
        pred_train = model.predict(X[indices])
        pred_test = model.predict(X[~indices])
        met = get_metrics(X[~indices], y[~indices], pred_test, protected_attribute_index)
        acc_train = accuracy_score(y[indices], pred_train)
        acc_test = accuracy_score(y[~indices], pred_test)
        subpop_train = calculate_subpopulation_accuracies(X[indices], y[indices], protected_attribute_index, model)
        subpop_test = calculate_subpopulation_accuracies(X[~indices], y[~indices], protected_attribute_index, model)
        stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
        stats.append(stat)
        losses.append(loss)
        accuracies_train.append(acc_train)
        accuracies_test.append(acc_test)
        subpop_train_list.append(subpop_train)
        subpop_test_list.append(subpop_test)
        all_metrics.append(met)
        tf.keras.backend.clear_session()
        gc.collect()
        
    return {
        "in_indices": in_indices_list,
        "stats": stats,
        "losses": losses,
        "subpop_train": subpop_train_list,
        "subpop_test": subpop_test_list,
        "accuracies_train": accuracies_train,
        "accuracies_test": accuracies_test,
        "all_metrics": all_metrics
    }

def train_models_syn(X, y, dataset_binary, protected_attribute_index, num_shadows=5,
                     model_builder=scikit_learn_model, transform_fn=synthetic):
    """
    Train models on a transformed (synthetic oversampled) dataset.
    Returns a dictionary with similar keys as train_models.
    """
    n_samples = X.shape[0]
    in_indices_list = []
    stats = []
    losses = []
    accuracies_train = []
    accuracies_test = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []
    
    for i in range(num_shadows + 1):
        indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
        in_indices_list.append(indices)
        
        dataset_train = dataset_binary.subset(indices)
        dataset_val = dataset_binary.subset(~indices)
        transformed_dataset_train = transform_fn(dataset_train,
                                                 dataset_binary.unprivileged_groups,
                                                 dataset_binary.base_rate(privileged=True),
                                                 dataset_binary.base_rate(privileged=False),
                                                 dataset_binary.favorable_label, dataset_binary.unfavorable_label, os_mode=2)
        X_train = transformed_dataset_train.features
        y_train = transformed_dataset_train.labels.ravel().astype(int)
        X_test = dataset_val.features
        y_test = dataset_val.labels.ravel().astype(int)
        
        model = model_builder()
        model.fit(X_train, y_train)
        pred_train = model.predict(X_train)
        pred_test = model.predict(X_test)
        met = get_metrics(X_test, y_test, pred_test, protected_attribute_index)
        all_metrics.append(met)
        acc_train = accuracy_score(y_train, pred_train)
        acc_test = accuracy_score(y_test, pred_test)
        accuracies_train.append(acc_train)
        accuracies_test.append(acc_test)
        subpop_train = calculate_subpopulation_accuracies(X[indices], y[indices], protected_attribute_index, model)
        subpop_test = calculate_subpopulation_accuracies(X[~indices], y[~indices], protected_attribute_index, model)
        subpop_train_list.append(subpop_train)
        subpop_test_list.append(subpop_test)
        stat, loss = get_stat_and_loss_tabular(model, X, y, use_proba=True)
        stats.append(stat)
        losses.append(loss)
        tf.keras.backend.clear_session()
        gc.collect()
        
    return {
        "in_indices": in_indices_list,
        "stats": stats,
        "losses": losses,
        "subpop_train": subpop_train_list,
        "subpop_test": subpop_test_list,
        "accuracies_train": accuracies_train,
        "accuracies_test": accuracies_test,
        "all_metrics": all_metrics
    }

def train_syn_target(X, y, dataset_binary, protected_attribute_index, num_shadows=5,
                     model_builder=scikit_learn_model):
    """
    Train models where one (the target) is trained on a synthetic dataset and the others on the original.
    Returns a dictionary with overall MIA results, subgroup MIA results, accuracies, and metrics.
    """
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []
    
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == 1) & (y == 1)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == 0) & (y == 1)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == 0) & (y == 0)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == 1) & (y == 0)),
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
                                                dataset_binary.unprivileged_groups,
                                                dataset_binary.base_rate(privileged=True),
                                                dataset_binary.base_rate(privileged=False),
                                                dataset_binary.favorable_label, dataset_binary.unfavorable_label, os_mode=2)
                X_train, y_train = transformed_dataset.features, transformed_dataset.labels.ravel()
                X_val, y_val = dataset_val.features, dataset_val.labels.ravel()
            else:
                X_train, y_train = X[train_indices], y[train_indices]
                X_val, y_val = X[val_indices], y[val_indices]
            
            model = model_builder()
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
        attack_input = AttackInputData(
            loss_train=scores[in_indices_target],
            loss_test=scores[~in_indices_target]
        )
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
            subgroup_attack_input = AttackInputData(
                loss_train=subgroup_scores[subgroup_in_indices_target],
                loss_test=subgroup_scores[~subgroup_in_indices_target]
            )
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
            
    overall_mean = float(np.round(np.mean(overall_results), 6))
    subgroup_means = {group: float(np.round(np.mean(vals), 6)) for group, vals in subgroup_results.items()}
    
    return {
        "overall_results": overall_results,
        "overall_mean": overall_mean,
        "subgroup_results": subgroup_results,
        "subgroup_means": subgroup_means,
        "train_accuracies": train_accuracies,
        "test_accuracies": test_accuracies,
        "subpop_train": subpop_train_list,
        "subpop_test": subpop_test_list,
        "all_metrics": all_metrics
    }

def train_rew_target(X, y, dataset_binary, protected_attribute_index, num_shadows=5,
                     model_builder=scikit_learn_model):
    """
    Train one target model on a reweighted dataset (using AIF360 Reweighing) and shadow models on the original data.
    Returns a dictionary with overall and subgroup MIA results, accuracies, and metrics.
    """
    n_samples = X.shape[0]
    overall_results = []
    subgroup_results = {}
    train_accuracies = []
    test_accuracies = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []
    
    RW = Reweighing(unprivileged_groups=dataset_binary.unprivileged_groups,
                    privileged_groups=dataset_binary.privileged_groups)
    
    subgroups = {
        'Privileged Favorable': ((X[:, protected_attribute_index] == 1) & (y == 1)),
        'Unprivileged Favorable': ((X[:, protected_attribute_index] == 0) & (y == 1)),
        'Unprivileged Unfavorable': ((X[:, protected_attribute_index] == 0) & (y == 0)),
        'Privileged Unfavorable': ((X[:, protected_attribute_index] == 1) & (y == 0)),
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
                reweighted_dataset = RW.fit_transform(dataset_train)
                X_train = reweighted_dataset.features
                y_train = reweighted_dataset.labels.ravel().astype(int)
                X_val = dataset_val.features
                y_val = dataset_val.labels.ravel().astype(int)
            else:
                X_train, y_train = X[train_indices], y[train_indices]
                X_val, y_val = X[val_indices], y[val_indices]
            
            model = model_builder()
            if i == target_idx:
                model.fit(X_train, y_train, sample_weight=reweighted_dataset.instance_weights)
            else:
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
        attack_input = AttackInputData(
            loss_train=scores[in_indices_target],
            loss_test=scores[~in_indices_target]
        )
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
            subgroup_attack_input = AttackInputData(
                loss_train=subgroup_scores[subgroup_in_indices_target],
                loss_test=subgroup_scores[~subgroup_in_indices_target]
            )
            subgroup_result = mia.run_attacks(subgroup_attack_input).single_attack_results[0]
            if group_name not in subgroup_results:
                subgroup_results[group_name] = []
            subgroup_results[group_name].append(subgroup_result.get_auc())
    overall_mean = float(np.round(np.mean(overall_results), 6))
    subgroup_means = {group: float(np.round(np.mean(vals), 6)) for group, vals in subgroup_results.items()}
    
    return {
        "overall_results": overall_results,
        "overall_mean": overall_mean,
        "subgroup_results": subgroup_results,
        "subgroup_means": subgroup_means,
        "train_accuracies": train_accuracies,
        "test_accuracies": test_accuracies,
        "subpop_train": subpop_train_list,
        "subpop_test": subpop_test_list,
        "all_metrics": all_metrics
    }

def train_models_eg(X, y, dataset_binary, protected_attribute_index, num_shadows=5,
                    model_builder=scikit_learn_model):
    """
    Train models using in-processing mitigation with ExponentiatedGradientReduction.
    X is a DataFrame and y is a NumPy array.
    Returns a dictionary with lists for in_indices, stats, losses, accuracies, and metrics.
    """
    n_samples = X.shape[0]
    in_indices_list = []
    stats = []
    losses = []
    accuracies_train = []
    accuracies_test = []
    subpop_train_list = []
    subpop_test_list = []
    all_metrics = []
    
    for i in range(num_shadows + 1):
        indices = np.random.binomial(1, 0.5, n_samples).astype(bool)
        in_indices_list.append(indices)
        train_X, train_y = X.iloc[indices], y[indices]
        test_X, test_y = X.iloc[~indices], y[~indices]
        
        model = model_builder()
        constraint = EqualizedOdds(difference_bound=0.001)
        mitigator = ExponentiatedGradientReduction(prot_attr=dataset_binary.protected_attribute_names[0],
                                                   estimator=model,
                                                   constraints=constraint)
        mitigator.fit(train_X, train_y)
        pred_train = mitigator.predict(train_X)
        pred_test = mitigator.predict(test_X)
        met = get_metrics(test_X.to_numpy(), test_y, pred_test, protected_attribute_index)
        all_metrics.append(met)
        acc_train = accuracy_score(train_y, pred_train)
        acc_test = accuracy_score(test_y, pred_test)
        accuracies_train.append(acc_train)
        accuracies_test.append(acc_test)
        subpop_train = calculate_subpopulation_accuracies(train_X, train_y, protected_attribute_index, mitigator)
        subpop_test = calculate_subpopulation_accuracies(test_X, test_y, protected_attribute_index, mitigator)
        subpop_train_list.append(subpop_train)
        subpop_test_list.append(subpop_test)
        stat, loss = get_stat_and_loss_tabular(mitigator, X, y, use_proba=True)
        stats.append(stat)
        losses.append(loss)
        tf.keras.backend.clear_session()
        gc.collect()
    return {
        "in_indices": in_indices_list,
        "stats": stats,
        "losses": losses,
        "subpop_train": subpop_train_list,
        "subpop_test": subpop_test_list,
        "accuracies_train": accuracies_train,
        "accuracies_test": accuracies_test,
        "all_metrics": all_metrics
    }

def average_dicts(dict_list):
    """Given a list of dictionaries, return a Series with the average for each key."""
    return pd.DataFrame(dict_list).mean()
