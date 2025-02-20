import imghdr

from django.core.exceptions import ValidationError
from rest_framework import serializers


class PassportImageSerializer(serializers.Serializer):
    image = serializers.FileField()

    def validate_image(self, value):
        # Check MIME type to ensure it's an image
        allowed_types = ['jpeg', 'png', 'gif', 'bmp', 'webp']
        file_type = imghdr.what(value)

        if file_type not in allowed_types:
            raise serializers.ValidationError("Only image files (JPEG, PNG, GIF, BMP, WebP) are allowed.")

        return value
