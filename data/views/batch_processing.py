import json
import uuid

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
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.models import BatchError, BatchUpload, SanctionedEntity
from data.serializers.batch_processing import FileUploadSerializer


class UploadDataView(APIView):
    """
    API endpoint to upload entities file
    """
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_serializer(self):
        return FileUploadSerializer()
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'JSON file containing entities data',
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="File processed successfully.",
                response={
                    "type": "object",
                    "properties": {
                        "batch_id": {"type": "string", "format": "uuid"},
                        "message": {"type": "string"},
                        "success_count": {"type": "integer"},
                        "errors": {"type": "integer"},
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
            500: OpenApiResponse(
                description="Internal Server Error",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "batch_id": {"type": "string", "format": "uuid"},
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                name="Successful Upload",
                value={
                    "batch_id": "123e4567-e89b-12d3-a456-426614174000",
                    "message": "File processed successfully.",
                    "success_count": 100,
                    "errors": 2,
                },
                status_codes=['200'],
            ),
            OpenApiExample(
                name="Invalid File Type",
                value={
                    "error": "Invalid file type. Only JSON files are allowed.",
                },
                status_codes=['400'],
            ),
        ],
    )
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith(".json"):
            return Response({"error": "Invalid file type. Only JSON files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new batch upload record
        batch_upload = BatchUpload.objects.create(
            batch_id=uuid.uuid4(),
            file_name=file.name,
            status='processing'
        )

        try:
            with transaction.atomic():
                line_number = 0
                success_count = 0

                for line in file:
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

                return Response({
                    "batch_id": batch_upload.batch_id,
                    "message": "File processed successfully.",
                    "success_count": success_count,
                    "errors": batch_upload.errors.count(),
                }, status=status.HTTP_200_OK)

        except Exception as e:
            batch_upload.status = 'failed'
            batch_upload.save()
            BatchError.objects.create(
                batch=batch_upload,
                error_message=f"Batch processing failed: {str(e)}"
            )
            return Response(
                {"error": str(e), "batch_id": batch_upload.batch_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BatchStatusView(APIView):
    """
    API endpoint to get the satus of uploading
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @extend_schema(
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