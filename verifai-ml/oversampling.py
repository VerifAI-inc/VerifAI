import numpy as np
import random
from aif360.metrics import utils

def group_indices(dataset, unprivileged_groups):
    """
    Returns indices of examples in the unprivileged and privileged groups.
    """
    feature_names = dataset.feature_names
    cond_vec = utils.compute_boolean_conditioning_vector(dataset.features, feature_names, unprivileged_groups)
    indices = [i for i, x in enumerate(cond_vec) if x]
    priv_indices = [i for i, x in enumerate(cond_vec) if not x]
    return indices, priv_indices

def balance(dataset, n_extra, inflate_rate, f_label, uf_label):
    """
    Oversample one of the groups using ADASYN and then select extra samples.
    """
    from imblearn.over_sampling import ADASYN
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
    new_weights = [random.choice(instance_weights_list) for _ in range(X.shape[0] - f_dataset.features.shape[0])]
    new_attributes = np.array([random.choice(protected_attributes_list) for _ in range(X.shape[0] - f_dataset.features.shape[0])]).reshape(-1, 1)
    
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
    dataset_transf_train = dataset.copy(deepcopy=True)
    if bp < bnp:
        dataset_transf_train = synthetic_balance(dataset, unprivileged_groups, bp, bnp, f_label, uf_label)
        return dataset_transf_train

    if os_mode == 1:
        _, sample_unfavor_priv = synthetic_unfavor_priv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_unfavor_priv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_unfavor_priv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_unfavor_priv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_unfavor_priv.protected_attributes))
    elif os_mode == 2:
        _, sample_favor_unpriv = synthetic_favor_unpriv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_favor_unpriv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_favor_unpriv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_favor_unpriv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_favor_unpriv.protected_attributes))
    elif os_mode == 3:
        _, sample_unfavor_priv = synthetic_unfavor_priv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_unfavor_priv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_unfavor_priv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_unfavor_priv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_unfavor_priv.protected_attributes))
        _, sample_favor_unpriv = synthetic_favor_unpriv(dataset, unprivileged_groups, bp, bnp, f_label, uf_label, sampling_strategy)
        dataset_transf_train.features = np.concatenate((dataset_transf_train.features, sample_favor_unpriv.features))
        dataset_transf_train.labels = np.concatenate((dataset_transf_train.labels, sample_favor_unpriv.labels))
        dataset_transf_train.instance_weights = np.concatenate((dataset_transf_train.instance_weights, sample_favor_unpriv.instance_weights))
        dataset_transf_train.protected_attributes = np.concatenate((dataset_transf_train.protected_attributes, sample_favor_unpriv.protected_attributes))
    else:
        raise ValueError("Oversampling mode is missing: os_mode must be 1, 2, or 3.")
    return dataset_transf_train
