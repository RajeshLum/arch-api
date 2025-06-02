from rest_framework import serializers
from data.amlmodels.verification_timeline_models import VerificationTimeline
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Simple User serializer for timeline entries"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class VerificationTimelineSerializer(serializers.ModelSerializer):
    """
    Serializer for the VerificationTimeline model.
    """
    performed_by = UserSerializer(read_only=True)
    formatted_date = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationTimeline
        exclude = ('verification',)  # Exclude verification to avoid circular reference
    
    def get_formatted_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_status_display(self, obj):
        status_map = {
            'pending': 'Pending',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'processing': 'Processing',
            'completed': 'Completed'
        }
        return status_map.get(obj.status, obj.status)
