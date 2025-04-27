import numpy as np
from scipy import special
from typing import Optional

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

    return -np.log(np.maximum(pred[np.arange(labels.size), labels.astype(int)], small_value)) * sample_weight

def calculate_statistic(probabilities: np.ndarray,
                        labels: np.ndarray,
                        sample_weight: Optional[np.ndarray] = None,
                        convert_to_prob: bool = False) -> np.ndarray:
    """
    Calculates, for each example, the probability assigned to the true class.
    """
    if convert_to_prob:
        probabilities = special.softmax(probabilities, axis=-1)
    stat = probabilities[np.arange(labels.size), labels.astype(int)]
    if sample_weight is not None:
        stat *= sample_weight
    return stat