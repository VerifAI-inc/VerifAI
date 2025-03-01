import pandas as pd
from aif360.datasets import BinaryLabelDataset
from sklearn.preprocessing import MinMaxScaler

def load_dataset(dataset_path: str, label_name, protected_attribute_name, unfavorable_label, favorable_label):
   
    dataframe = pd.read_csv(dataset_path)
    # Cpnvert Protected/Label to binaru, automatically extract unfav/unpriv
    dataset = BinaryLabelDataset(
    df=dataframe,
    label_names=[label_name],
    protected_attribute_names=[protected_attribute_name],
    favorable_label=favorable_label,
    unfavorable_label=unfavorable_label
)
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset.features = scaler.fit_transform(dataset.features)

    X = dataset.features
    y = dataset.labels.ravel().astype(int)
    
    protected_attribute_index = dataframe.columns.get_loc(protected_attribute_name)
    
    return X, y, protected_attribute_index, dataset, dataframe, protected_attribute_name, label_name
