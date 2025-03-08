# ml_modules/test_data.py
import os
import pickle
import pandas as pd
from aif360.datasets import BankDataset
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
from models import User, Session, UploadedDataset, UploadedModel

print("Django environment loaded successfully!")

DATA_PATH = os.path.join("ml_modules", "data", "bank_dataset.csv")
MODEL_PATH = os.path.join("ml_modules", "models", "random_forest_model.pkl")

# Function to create a mock user
def create_mock_user():
    """Creates a mock user for testing."""
    user, _ = User.objects.get_or_create(username="test_user", defaults={"password": "test123"})
    return user

# Function to load and preprocess dataset
def create_mock_dataset(user, session):
    # Store in database
    dataset_entry, _ = UploadedDataset.objects.get_or_create(
        user=user,
        session=session,
        name="bank_dataset.csv",
        label_name="y",
        pa_name="age",
        fav_label=1,
        priv_attb=1,  
        file=DATA_PATH
    )
    return dataset_entry

# Function to create a mock session
def create_mock_session(user):
    """Creates a mock session with fairness mitigator enabled."""
    session, _ = Session.objects.get_or_create(
        user=user,
        dp_model_type="RandomForestClassifier",
        dp_model_parameters={
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 4,
            "min_samples_leaf": 2,
            "bootstrap": True,
            "dp_epsilon": 1.0,  # Differential privacy parameter
            "dp_delta": 1e-5
        },
        mitigators="Reweighing",
        epsilon=1.0
    )
    return session

# Function to train & save RandomForest model
def create_mock_model(user, session):
    """Trains and saves a RandomForest model using the dataset."""
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Split dataset
    X = df.drop(columns=["y"])
    y = df["y"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train RandomForest model
    model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=4, min_samples_leaf=2, bootstrap=True)
    model.fit(X_train, y_train)

    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    # Store model info in database
    model_entry, _ = UploadedModel.objects.get_or_create(
        user=user,
        session=session,
        name="random_forest_model.pkl",
        file=MODEL_PATH
    )
    return model_entry

# Main function to create test data
def generate_test_data():
    """Runs all mock data generation functions."""
    user = create_mock_user()
    session = create_mock_session(user)
    dataset = create_mock_dataset(user, session)
    model = create_mock_model(user, session)

    print("✅ Test data created successfully!")
    print(f"User: {user.username}")
    print(f"Dataset saved at: {DATA_PATH}")
    print(f"Model saved at: {MODEL_PATH}")

# Run test data creation
if __name__ == "__main__":
    generate_test_data()