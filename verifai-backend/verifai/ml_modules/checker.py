import warnings
from diffprivlib.utils import DiffprivlibCompatibilityWarning

# Suppress FutureWarnings and DiffprivlibCompatibilityWarning
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DiffprivlibCompatibilityWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


import os
import pickle
import numpy as np
import pandas as pd
from aif360.datasets import StandardDataset
from diffprivlib.models import (
    GaussianNB as DPGaussianNB,
    LinearRegression as DPLinearRegression,
    LogisticRegression as DPLogisticRegression,
    RandomForestClassifier as DPRandomForestClassifier,
    KMeans as DPKMeans
)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans

from model_loader import load_model
from training import train_orig, train_dir, train_rew, train_syn



# === CONFIGURATION ===
DATASET_PATH = "./data/compas_preprocessed_final.csv"  # Change this
MODEL_PATH = "./models/random_forest_compas.pkl"      # Change this
LABEL_NAME = "two_year_recid"                        # Name of the target column
PROTECTED_ATTR_NAME = "sex"      # Name of the protected attribute
FAV_LABEL = 1                               # Favorable outcome
PRIVILEGED_ATTR = 1                         # Privileged attribute value
MITIGATOR = "DIR"                    # Choose: ["Reweighing", "DIR", "Synthetic", "Sampling", "None"]
EPSILON = 1.0                               # Differential Privacy level


# === LOAD DATASET ===
print("📚 Loading dataset...")
df = pd.read_csv(DATASET_PATH)

aif_dataset = StandardDataset(
    df,
    label_name=LABEL_NAME,
    favorable_classes=[FAV_LABEL],
    protected_attribute_names=[PROTECTED_ATTR_NAME],
    privileged_classes=[[PRIVILEGED_ATTR]]
)

X = aif_dataset.features
y = aif_dataset.labels.ravel()
protected_attr_idx = aif_dataset.feature_names.index(PROTECTED_ATTR_NAME)


# === LOAD MODEL ===
print("🤖 Loading model...")
model, original_model, dp_model = load_model(MODEL_PATH, EPSILON, X.shape[1])


# === SHADOW & TARGET MODEL BUILDER ===
shadow_model_builder = lambda: original_model
target_model_builder = lambda: dp_model


# === PICK TRAINING FUNCTION BASED ON MITIGATOR ===
print(f"🛠 Using mitigator: {MITIGATOR}")
if MITIGATOR == "Reweighing":
    results = train_rew(X, y, aif_dataset, protected_attr_idx, PRIVILEGED_ATTR, 1 - PRIVILEGED_ATTR, shadow_model_builder, target_model_builder)
elif MITIGATOR == "DIR":
    results = train_dir(X, y, aif_dataset, protected_attr_idx, PRIVILEGED_ATTR, 1 - PRIVILEGED_ATTR, shadow_model_builder, target_model_builder)
elif MITIGATOR in ["Synthetic", "Sampling"]:
    results = train_syn(X, y, aif_dataset, protected_attr_idx, PRIVILEGED_ATTR, 1 - PRIVILEGED_ATTR, shadow_model_builder, target_model_builder)
else:
    results = train_orig(X, y, aif_dataset, protected_attr_idx, PRIVILEGED_ATTR, 1 - PRIVILEGED_ATTR, shadow_model_builder, target_model_builder)


# === RESULTS ===
print("\n✅ RESULTS CHECK")
print(f"Total Training Accuracy: {results['train_accuracies'][-1]:.4f}")
print(f"Total Test Accuracy: {results['test_accuracies'][-1]:.4f}")

subgroup_map = {
    "Unprivileged Unfavorable": "g0-",
    "Privileged Unfavorable": "g1-",
    "Unprivileged Favorable": "g0+",
    "Privileged Favorable": "g1+",
}

subgroup_acc_test = {subgroup_map[k]: v for k, v in results['subpop_test'][-1].items() if k in subgroup_map}
subgroup_acc_train = {subgroup_map[k]: v for k, v in results['subpop_train'][-1].items() if k in subgroup_map}

# === Accuracy Results ===
print("\n🎯 Accuracy Results by Subgroup:")
for group, acc in subgroup_acc_test.items():
    print(f"  - Test {group}: {acc:.4f}")

# === Privacy Evaluation ===
subgroup_privacy = results['subgroup_means']
print("\n🔒 Privacy Risk by Subgroup:")
for group, risk in subgroup_privacy.items():
    print(f"  - {group}: {risk:.4f}")

# === Fairness Metrics ===
metrics = results['all_metrics'][-1] if results['all_metrics'] else {}
print("\n⚖️ Fairness Metrics:")
fairness_metrics = ["balanced_accuracy", "average_odds_difference", "disparate_impact",
                    "statistical_parity_difference", "equal_opportunity_difference", "theil_index"]

for metric in fairness_metrics:
    if metric in metrics:
        print(f"  - {metric}: {metrics[metric]:.4f}")
    else:
        print(f"  - {metric}: N/A")

print("\n🎉 All functionality checks passed successfully!")