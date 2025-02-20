import json
import threading
import uuid

import pyclamd
from django.apps import apps
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import (
    FileField,
    ModelSerializer,
    Serializer,
    ValidationError,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.models import BatchError, BatchUpload, SanctionedEntity


class FileUploadSerializer(Serializer):
    file = FileField()

    def validate_file(self, value):
        allowed_mime_types = ['application/json', 'text/csv']
        allowed_extensions = ['.json', '.csv']

        mime_type = value.content_type
        file_name = value.name.lower()

        if mime_type not in allowed_mime_types or not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise ValidationError("Only JSON and CSV files are allowed.")

        # Scan the file for viruses using ClamAV
        if self.scan_file(value):
            raise ValidationError("The uploaded file contains a virus and has been rejected.")

        return value

    def scan_file(self, file):
        """Scan the file using ClamAV"""
        try:
            clam = pyclamd.ClamdUnixSocket()
            if not clam.ping():
                raise Exception("ClamAV daemon is not running.")

            # Scan file data
            result = clam.scan_stream(file.read())
            file.seek(0)  # Reset file pointer after reading

            if result:
                return True  # File is infected

        except Exception as e:
            raise ValidationError(f"Virus scan error: {str(e)}")

        return False  # File is clean

class BatchUploadSerializer(ModelSerializer):
    class Meta:
        model = BatchUpload
        fields = ['batch_id', 'file_name', 'status', 'created_at', 'success_count']


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100


def process_file_async(file_content, batch_upload_id):
    """Process file content asynchronously"""
    try:
        # Get the batch upload object
        batch_upload = BatchUpload.objects.get(batch_id=batch_upload_id)
        batch_upload.status = 'processing'
        batch_upload.save()

        line_number = 0
        success_count = 0

        # Process each line in the file
        for line in file_content:
            line_number += 1
            try:
                # Decode and parse JSON line
                data = json.loads(line.decode("utf-8").strip())

                # Prepare SanctionedEntity data
                sanctioned_entity_data = {
                    "sanctionId": data.get("id"),
                    "caption": data.get("caption"),
                    "schema": data.get("schema"),
                    "referents": data.get("referents"),
                    "datasets": data.get("datasets"),
                    "first_seen": data.get("first_seen"),
                    "last_seen": data.get("last_seen"),
                    "last_change": data.get("last_change"),
                    "target": data.get("target", False),
                }

                # Use a transaction for each entity to ensure consistency
                with transaction.atomic():
                    # Create or update SanctionedEntity
                    sanctioned_entity, created = SanctionedEntity.objects.update_or_create(
                        sanctionId=sanctioned_entity_data["sanctionId"],
                        defaults=sanctioned_entity_data,
                    )

                    # Handle related schema-specific models
                    model_path = f"data.{data.get('schema')}"
                    ModelClass = apps.get_model(model_path)
                    model_data = data.get("properties", {})
                    ModelClass.objects.update_or_create(
                        sanctionEntity=sanctioned_entity,
                        defaults=model_data,
                    )

                success_count += 1
            except json.JSONDecodeError:
                BatchError.objects.create(
                    batch=batch_upload,
                    line_number=line_number,
                    error_message="Invalid JSON format"
                )
            except Exception as e:
                BatchError.objects.create(
                    batch=batch_upload,
                    line_number=line_number,
                    error_message=str(e)
                )

        # Update batch upload record
        batch_upload.status = 'completed'
        batch_upload.success_count = success_count
        batch_upload.save()

    except Exception as e:
        # Handle overall processing failure
        try:
            batch_upload = BatchUpload.objects.get(batch_id=batch_upload_id)
            batch_upload.status = 'failed'
            batch_upload.save()
            BatchError.objects.create(
                batch=batch_upload,
                error_message=f"Batch processing failed: {str(e)}"
            )
        except Exception:
            # Log this somewhere if even the error handling fails
            pass


class UploadDataView(APIView):
    """
    API endpoint to upload entities file
    """
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_serializer(self):
        return FileUploadSerializer()
    
    @extend_schema(
        summary="Get batch upload history",
        parameters=[
            OpenApiParameter(name="page", description="Page number", required=False, type=int),
            OpenApiParameter(name="page_size", description="Number of results per page", required=False, type=int),
        ],
        responses={
            200: BatchUploadSerializer(many=True),
        },
        tags=["Batch Processing"]
    )
    def get(self, request):
        paginator = self.pagination_class()
        batches = BatchUpload.objects.all().order_by('-created_at')
        page = paginator.paginate_queryset(batches, request)
        serializer = BatchUploadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @extend_schema(
        summary="Upload ftm.json file as batch",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'JSON or CSV file containing entities data',
                    }
                }
            }
        },
        responses={
            202: OpenApiResponse(
                description="File accepted for processing.",
                response={
                    "type": "object",
                    "properties": {
                        "batch_id": {"type": "string", "format": "uuid"},
                        "message": {"type": "string"},
                        "status": {"type": "string"},
                    }
                }
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                name="Successful Upload",
                value={
                    "batch_id": "123e4567-e89b-12d3-a456-426614174000",
                    "message": "File accepted for processing.",
                    "status": "queued",
                },
                status_codes=['202'],
            ),
            OpenApiExample(
                name="Invalid File Type",
                value={
                    "error": "Only JSON and CSV files are allowed.",
                },
                status_codes=['400'],
            ),
        ],
    tags=["Batch Processing"]
    )
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']

        # Create a new batch upload record
        batch_upload = BatchUpload.objects.create(
            batch_id=uuid.uuid4(),
            file_name=file.name,
            status='queued'
        )

        # Start asynchronous processing in a separate thread
        # Note: We need to read the file content now since the file handle
        # won't be available in the separate thread
        file_content = list(file)
        thread = threading.Thread(
            target=process_file_async,
            args=(file_content, batch_upload.batch_id)
        )
        thread.daemon = True  # Daemon threads don't block application shutdown
        thread.start()

        return Response({
            "batch_id": batch_upload.batch_id,
            "message": "File accepted for processing.",
            "status": "queued"
        }, status=status.HTTP_202_ACCEPTED)
        
        

class BatchStatusView(APIView):
    """
    API endpoint to get the satus of uploading
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Get the status of batch upload",
        parameters=[
            OpenApiParameter(
                name='batch_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the batch upload',
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Batch status retrieved successfully.",
                response={
                    "type": "object",
                    "properties": {
                        "batch_id": {"type": "string", "format": "uuid"},
                        "status": {"type": "string"},
                        "file_name": {"type": "string"},
                        "success_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "errors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "line_number": {"type": "integer"},
                                    "error_message": {"type": "string"},
                                }
                            }
                        },
                    }
                }
            ),
            404: OpenApiResponse(
                description="Not Found",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                name="Batch Status",
                value={
                    "batch_id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "completed",
                    "file_name": "entities.json",
                    "success_count": 100,
                    "created_at": "2023-10-01T12:34:56Z",
                    "updated_at": "2023-10-01T12:35:10Z",
                    "errors": [
                        {"line_number": 5, "error_message": "Invalid JSON format"},
                        {"line_number": 10, "error_message": "Missing required field"},
                    ],
                },
                status_codes=['200'],
            ),
            OpenApiExample(
                name="Batch Not Found",
                value={
                    "error": "Batch ID not found.",
                },
                status_codes=['404'],
            ),
        ],
        
    tags=["Batch Processing"]
    )
    def get(self, request, batch_id):
        try:
            batch_upload = BatchUpload.objects.get(batch_id=batch_id)
            return Response({
                "batch_id": batch_upload.batch_id,
                "status": batch_upload.status,
                "file_name": batch_upload.file_name,
                "success_count": batch_upload.success_count,
                "created_at": batch_upload.created_at,
                "updated_at": batch_upload.updated_at,
                "errors": list(batch_upload.errors.values('line_number', 'error_message'))
            }, status=status.HTTP_200_OK)
        except BatchUpload.DoesNotExist:
            return Response(
                {"error": "Batch ID not found."},
                status=status.HTTP_404_NOT_FOUND
            )