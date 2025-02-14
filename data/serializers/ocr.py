from rest_framework import serializers, status


class PassportImageSerializer(serializers.Serializer):
    image = serializers.FileField()