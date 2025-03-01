import pandas as pd
from aif360.datasets import BinaryLabelDataset
from sklearn.preprocessing import MinMaxScaler

def load_dataset(dataset_path: str, label_name, protected_attribute_name, favorable_label, privileged_attribute):

    # Load dataset
    dataframe = pd.read_csv(dataset_path)

    # Convert label column: Favorable label → 1, Others → 0
    dataframe[label_name] = (dataframe[label_name] == favorable_label).astype(int)

    # Convert protected attribute: Privileged attribute → 1, Others → 0
    dataframe[protected_attribute_name] = (dataframe[protected_attribute_name] == privileged_attribute).astype(int)

    # Convert to AIF360 BinaryLabelDataset
    dataset = BinaryLabelDataset(
        df=dataframe,
        label_names=[label_name],
        protected_attribute_names=[protected_attribute_name],
        favorable_label=1,
        unfavorable_label=0 
    )

    # Normalize features using Min-Max Scaling
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset.features = scaler.fit_transform(dataset.features)

    # Extract feature matrix (X) and target variable (y)
    X = dataset.features
    y = dataset.labels.ravel().astype(int)

    # Get the index of the protected attribute in the dataframe
    protected_attribute_index = dataframe.columns.get_loc(protected_attribute_name)

    return X, y, protected_attribute_index, dataset, dataframe, protected_attribute_name, label_name
