from rest_framework import serializers
from data.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'organization', 'dob', 'gender', 'photo', 'two_fa_enabled']
