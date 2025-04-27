# webapp/serializers.py
from rest_framework import serializers
from .models import ReportHistory
import os
from django.core.files.storage import default_storage
from rest_framework import serializers
from .models import Session, UploadedModel, UploadedDataset

class ReportHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportHistory
        # Return the fields that the frontend will need
        fields = ['id', 'name', 'content', 'creation_date']


class UploadSerializer(serializers.Serializer):
    modelFile = serializers.FileField()
    datasetFile = serializers.FileField()
    labelName = serializers.CharField(max_length=255)
    favorableLabel = serializers.FloatField()
    protectedAttribute = serializers.CharField(max_length=255)
    privilegedAttribute = serializers.FloatField()
    mitigators = serializers.ListField(
        child=serializers.CharField(max_length=255),
        allow_empty=True,
        required=False
    )
    dpModel = serializers.CharField(max_length=255, default="example")
    epsilon = serializers.FloatField(default=1.0)

    def validate_modelFile(self, value):
        """
        Validate that the model file has a valid extension.
        It must end with 'pickle' or 'pkl'.
        """
        filename = value.name.lower()
        if not (filename.endswith(".pickle") or filename.endswith(".pkl")):
            raise serializers.ValidationError("Model file must have a .pickle or .pkl extension.")
        return value

    def validate_datasetFile(self, value):
        """
        Validate that the dataset file has a CSV extension.
        """
        if not value.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Dataset file must have a .csv extension.")
        return value

    def create(self, validated_data):
        # Retrieve the user from the serializer context (set in the view)
        user = self.context['request'].user
        

        # Extract file objects and additional fields
        model_file = validated_data.pop('modelFile')
        dataset_file = validated_data.pop('datasetFile')
        label_name = validated_data.pop('labelName')
        favorable_label = validated_data.pop('favorableLabel')
        protected_attribute = validated_data.pop('protectedAttribute')
        privileged_attribute = validated_data.pop('privilegedAttribute')
        mitigators = validated_data.pop('mitigators', [])
        dp_model = validated_data.pop('dpModel')
        epsilon = validated_data.pop('epsilon', 1.0)

        # ---------------------------
        # Create a Session record
        # ---------------------------
        session = Session.objects.create(
            user=user,
            dp_model_type=dp_model,
            dp_model_parameters={},  # Adjust if you need additional parameters
            mitigators=",".join(mitigators),
            epsilon=epsilon
        )

        # ---------------------------
        # Generate custom file names and save files
        # ---------------------------
        model_filename = f"{session.id}_{model_file.name}"
        dataset_filename = f"{session.id}_{dataset_file.name}"

        model_path = default_storage.save(os.path.join("models", model_filename), model_file)
        dataset_path = default_storage.save(os.path.join("datasets", dataset_filename), dataset_file)

        # ---------------------------
        # Create UploadedModel and UploadedDataset records
        # ---------------------------
        UploadedModel.objects.create(
            user=user,
            session=session,
            name=model_filename,
            file=model_path
        )

        UploadedDataset.objects.create(
            user=user,
            session=session,
            name=dataset_filename,
            label_name=label_name,
            pa_name=protected_attribute,
            fav_label=favorable_label,
            priv_attb=privileged_attribute,
            file=dataset_path
        )

        return session
