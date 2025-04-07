import pandas as pd
from aif360.datasets import BinaryLabelDataset
from sklearn.preprocessing import MinMaxScaler

def load_dataset(dataset_path: str, label_name, protected_attribute_name, favorable_label):
    dataframe = pd.read_csv(dataset_path)

    # Ensure the label column is categorical for consistency
    dataframe[label_name] = dataframe[label_name].astype(str)
    favorable_label = str(favorable_label)  # Ensure consistency in string format

    unique_labels = dataframe[label_name].unique()
    unfavorable_candidates = unique_labels[unique_labels != str(favorable_label)]
    if len(unfavorable_candidates) != 1:
        raise ValueError("There must be exactly one unfavorable label.")
    unfavorable_label = unfavorable_candidates[0]


    # Convert dataset to BinaryLabelDataset
    dataset = BinaryLabelDataset(
        df=dataframe,
        label_names=[label_name],
        protected_attribute_names=[protected_attribute_name],
        favorable_label=favorable_label,
        unfavorable_label=unfavorable_label
    )

    # Normalize feature values
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset.features = scaler.fit_transform(dataset.features)

    # Extract X (features), y (labels), and protected attribute index
    X = dataset.features
    y = dataset.labels.ravel().astype(int)
    protected_attribute_index = dataframe.columns.get_loc(protected_attribute_name)

    return X, y, protected_attribute_index, dataset, dataframe, protected_attribute_name, label_name