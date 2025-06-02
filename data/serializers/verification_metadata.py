from rest_framework import serializers
from data.amlmodels.verification_metadata_models import VerificationMetadata

class VerificationMetadataSerializer(serializers.ModelSerializer):
    """
    Serializer for the VerificationMetadata model.
    """
    class Meta:
        model = VerificationMetadata
        exclude = ('verification',)  # Exclude verification to avoid circular reference
