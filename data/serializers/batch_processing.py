
from rest_framework.serializers import FileField, Serializer


class FileUploadSerializer(Serializer):
    file = FileField()