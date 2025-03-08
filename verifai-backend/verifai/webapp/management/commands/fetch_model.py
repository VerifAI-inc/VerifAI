import os
import pickle
from django.core.management.base import BaseCommand
from django.conf import settings
from webapp.models import UploadedModel, Session
from ml_modules.model_loader import load_model

class Command(BaseCommand):
    help = "Fetch model metadata and load it for processing"

    def handle(self, *args, **kwargs):
        model_name = "random_forest_model.pkl"  

        try:
            # Fetch model entry from the database
            uploaded_model = UploadedModel.objects.get(name=model_name)
            model_path = os.path.join(settings.MEDIA_ROOT, str(uploaded_model.file))

            # Fetch corresponding session for DP parameters
            session = uploaded_model.session
            epsilon = session.epsilon  # Get DP epsilon from session
            
            self.stdout.write(self.style.SUCCESS("📌 Model Metadata:"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Model Path: {model_path}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Epsilon: {epsilon}"))

            # Load model from file
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            num_features = len(model.feature_importances_) if hasattr(model, "feature_importances_") else None

            self.stdout.write(self.style.SUCCESS(f"   🔹 Model Type: {model.__class__.__name__}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Model Parameters: {model.get_params()}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Number of Features: {num_features}"))

            # ✅ Load the original & DP models
            model, original_model, dp_model = load_model(
                file_path=model_path,
                epsilon=epsilon,
                num_features=num_features
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Model Loaded Successfully!"))

        except UploadedModel.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"❌ Model '{model_name}' not found in the database."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️ Error: {e}"))