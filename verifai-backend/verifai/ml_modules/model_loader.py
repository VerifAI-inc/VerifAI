import pickle
import numpy as np

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

def load_model(file_path: str, epsilon, num_features):
    with open(file_path, 'rb') as f:
        model = pickle.load(f)

    if not hasattr(model, "get_params") or not hasattr(model, "__class__") or not getattr(model.__class__, "__name__", None):
        raise ValueError("Uploaded model should be a scikit-learn model with a get_params() method and a valid class name.")

    model_name = model.__class__.__name__
    params = model.get_params()

    supported_models = {
        "LogisticRegression", "DecisionTreeClassifier",
        "RandomForestClassifier", "GaussianNB",
        "LinearRegression", "KMeans"
    }

    # if model_name not in supported_models:
    #     raise ValueError(f"Unsupported model type: {model_name}. Please upload a valid scikit-learn model that IBM supports.")

    # Create a temporary DP model to check valid parameters
    dp_model_class = {
    "RandomForestClassifier": DPRandomForestClassifier,
    "LinearRegression": DPLinearRegression,
    "GaussianNB": DPGaussianNB,
    "LogisticRegression": DPLogisticRegression,
    "KMeans": DPKMeans
    }.get(model_name, DPRandomForestClassifier)


    if dp_model_class:
        # Get valid DP model parameters
        dp_valid_params = set(dp_model_class().get_params().keys())
        original_params = set(params.keys())

        # Remove non-functional parameters
        non_functional_params = original_params - dp_valid_params
        for param in non_functional_params:
            params.pop(param, None)

    # ✅ Handle `random_state` correctly
    if "random_state" in params and params["random_state"] is None:
        params["random_state"] = 42  # Default to 42 if not set by user

    # ✅ Create Original & DP Model
    original_model, dp_model = None, None
    if model_name == "RandomForestClassifier":
        original_model = RandomForestClassifier(**params)
        dp_model = DPRandomForestClassifier(**params, epsilon=epsilon, bounds=(0, 1), classes=[0, 1])
    elif model_name == "LinearRegression":
        original_model = LinearRegression(**params)
        dp_model = DPLinearRegression(**params, epsilon=epsilon, bounds_X=(0, 1), bounds_y=(0, 1))
    elif model_name == "GaussianNB":
        original_model = GaussianNB(**params)
        dp_model = DPGaussianNB(**params, epsilon=epsilon, bounds=(0, 1))
    elif model_name == "LogisticRegression":
        original_model = LogisticRegression(**params)
        dp_model = DPLogisticRegression(**params, epsilon=epsilon, data_norm=np.sqrt(num_features))
    elif model_name == "KMeans":
        original_model = KMeans(**params)
        dp_model = DPKMeans(**params, n_clusters=params["n_clusters"], epsilon=epsilon, bounds=(0, 1))
    else:
        original_model = model.__class__(**params)
        dp_model = DPRandomForestClassifier(epsilon=epsilon, bounds=(0, 1), classes=[0, 1])

    

    return model, original_model, dp_model