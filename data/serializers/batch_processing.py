from rest_framework.serializers import FileField, Serializer, ValidationError


class FileUploadSerializer(Serializer):
    file = FileField()

    def validate_file(self, value):
        allowed_mime_types = ['application/json', 'text/csv']
        allowed_extensions = ['.json', '.csv']
        
        mime_type = value.content_type
        file_name = value.name.lower()

        if mime_type not in allowed_mime_types or not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise ValidationError("Only JSON and CSV files are allowed.")

        return value
