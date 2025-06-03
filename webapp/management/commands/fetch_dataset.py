from django.core.management.base import BaseCommand
from webapp.models import UploadedDataset
from ml_modules.data_loader import load_dataset  # Import the function
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Fetch dataset metadata and load it for processing"

    def handle(self, *args, **kwargs):
        dataset_name = "bank_dataset.csv"  # Default dataset name
        try:
            # Fetch dataset metadata from the database
            dataset = UploadedDataset.objects.get(name=dataset_name)
            dataset_path = os.path.join(settings.MEDIA_ROOT, str(dataset.file))

            label_name = dataset.label_name
            protected_attribute_name = dataset.pa_name
            favorable_label = dataset.fav_label  # Dynamically get the favorable label from DB

            self.stdout.write(self.style.SUCCESS(f"📌 Dataset Metadata:"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Path: {dataset_path}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Label Name: {label_name}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Protected Attribute: {protected_attribute_name}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Favorable Label: {favorable_label}"))

            # ✅ Call the updated load_dataset() function
            X, y, protected_attribute_index, dataset_binary, dataframe, protected_attribute_name, label_name = load_dataset(
                dataset_path=dataset_path,
                label_name=label_name,
                protected_attribute_name=protected_attribute_name,
                favorable_label=favorable_label
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Dataset Loaded Successfully!"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Feature Shape: {X.shape}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Label Shape: {y.shape}"))
            self.stdout.write(self.style.SUCCESS(f"   🔹 Protected Attribute Index: {protected_attribute_index}"))

        except UploadedDataset.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"❌ Dataset '{dataset_name}' not found in the database."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"⚠️ Error: {e}"))