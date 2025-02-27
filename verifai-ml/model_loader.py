import pickle
import numpy as np

from diffprivlib.models import GaussianNB as DPGaussianNB
from diffprivlib.models import LinearRegression as DPLinearRegression
from diffprivlib.models import LogisticRegression as DPLogisticRegression
from diffprivlib.models import RandomForestClassifier as DPRandomForestClassifier
from diffprivlib.models import KMeans as DPKMeans

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
        # Classification models
        "LogisticRegression", "DecisionTreeClassifier",
        "RandomForestClassifier", "GaussianNB",

        # Regression models
        "LinearRegression",

        # Clustering models
        "KMeans"
    }

    if model_name not in supported_models:
        raise ValueError(f"Unsupported model type: {model_name}. Please upload a valid scikit-learn model that IBM supports")


    # Based on the model name, create the corresponding DP model.
    if model_name == "RandomForestClassifier":
        original_model = RandomForestClassifier(**params)
        dp_model = DPRandomForestClassifier(**params, epsilon = epsilon, bounds=(0, 1), classes = [0,1], random_state=42)
    elif model_name == "LinearRegression":
        original_model = LinearRegression(**params)
        dp_model = DPLinearRegression(**params, epsilon = epsilon, bounds_X=(0, 1), bounds_y=(0, 1), random_state=42)
    elif model_name == "GaussianNB":
        original_model = GaussianNB(**params)
        dp_model = DPGaussianNB(**params, epsilon = epsilon, bounds=(0, 1))
    elif model_name == "LogisticRegression":
        original_model = LogisticRegression(**params)
        dp_model = DPLogisticRegression(**params, epsilon = epsilon, data_norm=np.sqrt(num_features))
    elif model_name == "KMeans":
        original_model = KMeans(**params)
        dp_model = DPKMeans(**params, n_clusters =params[n_clusters] , epsilon = epsilon, bounds=(0, 1))
    else:
        raise ValueError(f"DP model for name '{model_name}' is not supported.")
    
    return model, original_model, dp_model
