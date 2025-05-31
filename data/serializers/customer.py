from rest_framework import serializers
from data.models import Customer, Identity, Employability, BankInfo, CustomerAdditionalInfo, BusinessInfo

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Customer
        exclude = []
        read_only_fields = ['user']
        
    def validate_first_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value
    
    def validate_photo(self, value):
        max_size = 5 * 1024 * 1024  # 5MB
        allowed_types = ['image/jpeg', 'image/png']

        file_name = value.name.lower()
        
        if value.size > max_size:
            raise serializers.ValidationError("Photo must be smaller than 5MB.")

        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG and PNG images are allowed.")

        return value

class IdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Identity
        fields = '__all__'

class EmployabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employability
        fields = '__all__'

class BankInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankInfo
        fields = '__all__'
        
class CustomerAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAdditionalInfo
        fields = '__all__'

class BusinessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = '__all__'
