import os
import django
from django.conf import settings
from models import UploadedDataset

# Ensure Django settings are initialized
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "verifai.settings")
django.setup()

def get_dataset_metadata(dataset_name):
    """
    Fetch dataset metadata from UploadedDataset table.
    
    :param dataset_name: Name of the dataset file (e.g., "bank_dataset.csv").
    :return: Dictionary containing metadata (file path, label, protected attribute, etc.)
    """
    try:
        dataset = UploadedDataset.objects.get(name=dataset_name)  # Query DB
        dataset_path = os.path.join(settings.MEDIA_ROOT, str(dataset.file))  # Get absolute path

        metadata = {
            "dataset_path": dataset_path,
            "label_name": dataset.label_name,
            "protected_attribute_name": dataset.pa_name,
            "fav_label": dataset.fav_label,
            "priv_attb": dataset.priv_attb,
        }
        
        return metadata

    except UploadedDataset.DoesNotExist:
        print(f"❌ Dataset '{dataset_name}' not found in database.")
        return None
    except Exception as e:
        print(f"⚠️ Error retrieving dataset metadata: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    dataset_metadata = get_dataset_metadata("bank_dataset.csv")
    print("📌 Dataset Metadata:", dataset_metadata)