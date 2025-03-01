# ml_modules/test_data.py
from webapp.models import User, Session, UploadedModel, UploadedDataset

def create_mock_user():
    """Creates a mock user for testing."""
    user, _ = User.objects.get_or_create(username="test_user", defaults={"password": "test123"})
    return user

def create_mock_session(user):
    """Creates a mock session with fairness mitigator enabled."""
    session, _ = Session.objects.get_or_create(
        user=user,
        dp_model_type="RandomForestClasifier",
        dp_model_parameters={},
        mitigators="Reweighing",
        epsilon=1.0  # Default epsilon value
    )
    return session