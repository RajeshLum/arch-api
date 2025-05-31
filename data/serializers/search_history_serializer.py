from rest_framework import serializers
from data.amlmodels.search_history_model import SearchHistory
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class SearchHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'query', 'result_count', 'filters', 'created_at']
        read_only_fields = ['id', 'created_at']
        
    def create(self, validated_data):
        # Get the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
