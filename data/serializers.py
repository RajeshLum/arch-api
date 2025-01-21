from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers


class TransactionDetailsSerializer(serializers.Serializer):
    volume = serializers.FloatField(required=False)
    frequency = serializers.IntegerField(required=False)

class EntityDetailsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    date_of_birth = serializers.DateField(required=False)
    nationality = serializers.CharField(max_length=100)
    id_number = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=500)

class RiskScoringRequestSerializer(serializers.Serializer):
    entity = EntityDetailsSerializer()
    transactions = TransactionDetailsSerializer(required=False)

class RiskScoreBreakdownSerializer(serializers.Serializer):
    sanctions_match = serializers.FloatField()
    # pep = serializers.FloatField()
    geography = serializers.FloatField()
    adverse_media = serializers.FloatField()
    transactions = serializers.FloatField()

class RiskScoringResponseSerializer(serializers.Serializer):
    entity_id = serializers.CharField()
    risk_score = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    risk_category = serializers.CharField()
    reasons = serializers.ListField(child=serializers.CharField())
    breakdown = RiskScoreBreakdownSerializer()
