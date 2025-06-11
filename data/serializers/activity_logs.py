from rest_framework import serializers
from data.models import ActivityLogs

class ActivityLogsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ActivityLogs # fields = '__all__'
        fields = [
            'id', 'activity', 'description', 'ip_address', 'country', 'city',
            'browser', 'browser_version', 'os', 'device', 'status',
            'created_at', 'updated_at', 'user'
        ]
