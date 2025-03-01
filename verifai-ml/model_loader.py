import pickle

def load_model(model_file_path: str):
    """
    Loads a model from a pickle file.
    
    Args:
        model_file_path: Path to the pickle file containing the model.
    
    Returns:
        The loaded model.
    
    Raises:
        ValueError: If the model does not have a 'predict' method.
    """
    with open(model_file_path, 'rb') as f:
        model = pickle.load(f)
    if not hasattr(model, 'predict'):
        raise ValueError("The loaded model does not implement a 'predict' method.")
    return model
