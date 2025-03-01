import pandas as pd
from aif360.datasets import BinaryLabelDataset

def load_csv_dataset(csv_file_path: str, 
                     protected_attribute_name: str,
                     target_name: str,
                     favorable_label,
                     unfavorable_label,
                     privileged_value,
                     unprivileged_value):
    """
    Loads a cleaned CSV file and creates a BinaryLabelDataset.
    
    Args:
      csv_file_path: Path to the CSV file.
      protected_attribute_name: Name of the protected attribute column.
      target_name: Name of the target label column.
      favorable_label: Value in the target column considered favorable.
      unfavorable_label: Value in the target column considered unfavorable.
      privileged_value: Value in the protected attribute column that denotes the privileged group.
      unprivileged_value: Value in the protected attribute column that denotes the unprivileged group.
      
    Returns:
      A dictionary containing:
         - 'X': Features (numpy array) excluding the target column.
         - 'y': Target labels (numpy array).
         - 'protected_attribute_index': Index of the protected attribute column.
         - 'dataset_binary': The BinaryLabelDataset instance.
         - 'df': The original DataFrame.
         - 'protected_attribute_name': The protected attribute name.
         - 'target_name': The target column name.
         - 'privileged_groups': List of privileged group dict.
         - 'unprivileged_groups': List of unprivileged group dict.
    """
    df = pd.read_csv(csv_file_path)
    # Validate required columns exist
    if protected_attribute_name not in df.columns:
        raise ValueError(f"Protected attribute '{protected_attribute_name}' not found in dataset.")
    if target_name not in df.columns:
        raise ValueError(f"Target attribute '{target_name}' not found in dataset.")
    
    # Create the AIF360 dataset
    dataset_binary = BinaryLabelDataset(
        favorable_label=favorable_label,
        unfavorable_label=unfavorable_label,
        df=df,
        label_names=[target_name],
        protected_attribute_names=[protected_attribute_name]
    )
    
    X = dataset_binary.features
    y = dataset_binary.labels.ravel()
    protected_attribute_index = df.columns.get_loc(protected_attribute_name)
    
    privileged_groups = [{protected_attribute_name: privileged_value}]
    unprivileged_groups = [{protected_attribute_name: unprivileged_value}]
    
    return {
        "X": X,
        "y": y,
        "protected_attribute_index": protected_attribute_index,
        "dataset_binary": dataset_binary,
        "df": df,
        "protected_attribute_name": protected_attribute_name,
        "target_name": target_name,
        "privileged_groups": privileged_groups,
        "unprivileged_groups": unprivileged_groups
    }