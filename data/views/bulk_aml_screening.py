import os
import csv
import uuid
import pandas as pd
from io import StringIO
from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

from data.amlmodels.bulk_aml_screening_models import BulkAmlScreening, BulkAmlScreeningRecord
from data.amlmodels.verification_models import Verification
from data.amlmodels.verification_metadata_models import VerificationInfo
from data.amlmodels.verification_timeline_models import VerificationTimeline
from data.utils.reference_generator import generate_reference_id
from data.utils.geolocation import get_user_country, get_client_ip
from data.utils.user_agent_parser import parse_user_agent

from data.tasks.bulk_aml_screening_tasks import process_bulk_aml_screening


class BulkAmlScreeningView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Upload and process a bulk AML screening file
        """
        try:
            # Check if file is provided
            if 'file' not in request.FILES:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            
            # Check file type
            file_name = file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            
            if file_extension not in ['.csv', '.xlsx', '.xls']:
                return Response({"error": "Only CSV and Excel files are supported"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the file
            uuid_str = str(uuid.uuid4())
            short_uuid = uuid_str[:16]
            saved_file_name = f"{short_uuid}_{file_name}"
            file_path = default_storage.save(f'uploads/bulk_aml_screening/{saved_file_name}', ContentFile(file.read()))
            
            # Parse countries and models from request
            countries = request.data.get('countries', '[]')
            screening_models = request.data.get('screening_models', '[]')
            
            # Parse additional options
            is_manual_review = request.data.get('is_manual_review', 'false').lower() in ['true', 'yes', '1']
            decline_on_single_step = request.data.get('decline_on_single_step', 'false').lower() in ['true', 'yes', '1']
            check_family = request.data.get('check_family', 'false').lower() in ['true', 'yes', '1']
            
            # Count total records in the file
            total_records = 0
            try:
                if file_extension == '.csv':
                    with default_storage.open(file_path, 'r') as f:
                        reader = csv.reader(f)
                        # Skip header
                        next(reader, None)
                        total_records = sum(1 for row in reader)
                else:  # Excel file
                    file_content = default_storage.open(file_path, 'rb').read()
                    df = pd.read_excel(file_content)
                    total_records = len(df)
            except Exception as e:
                return Response({"error": f"Error parsing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create bulk screening record - only store file metadata
            bulk_screening = BulkAmlScreening.objects.create(
                user=request.user,
                file_name=file_name,
                file_path=file_path,
                total_records=total_records,
                processed_records=0,
                status='pending'  # Set initial status
            )
            
            # Start processing task asynchronously
            # In a production environment, this would be handled by Celery or similar
            # For now, we'll process it synchronously
            process_bulk_aml_screening(bulk_screening.id)
            
            return Response({
                "message": "File uploaded successfully",
                "data": {
                    "id": bulk_screening.id,
                    "reference_id": bulk_screening.reference_id,
                    "file_name": bulk_screening.file_name,
                    "total_records": bulk_screening.total_records,
                    "status": bulk_screening.status,
                    "created_at": bulk_screening.created_at
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkAmlScreeningHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get bulk AML screening history for the authenticated user
        """
        try:
            # Get page and limit parameters
            try:
                page = int(request.query_params.get('page', 1))
            except (TypeError, ValueError):
                page = 1
                
            try:
                page_size = int(request.query_params.get('limit', 20))
                # Cap page size to reasonable limits
                page_size = min(max(page_size, 1), 100)  # Between 1 and 100
            except (TypeError, ValueError):
                page_size = 20
            
            # Filter by user unless admin
            if request.user.is_staff:
                queryset = BulkAmlScreening.objects.all().order_by('-created_at')
            else:
                queryset = BulkAmlScreening.objects.filter(user=request.user).order_by('-created_at')
            
            # Apply pagination
            paginator = PageNumberPagination()
            paginator.page_size = page_size
            paginated_qs = paginator.paginate_queryset(queryset, request)
            
            # Format response data
            history_data = []
            for item in paginated_qs:
                history_data.append({
                    "id": item.id,
                    "reference_id": item.reference_id,
                    "fileName": item.file_name,
                    "uploadDate": item.created_at,
                    "totalRecords": item.total_records,
                    "processedRecords": item.processed_records,
                    "status": item.status,
                    "updated_at": item.updated_at
                })
            
            return Response({
                "message": "History retrieved successfully",
                "data": history_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": queryset.count()
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkAmlScreeningDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, bulk_id):
        """
        Get details of a specific bulk AML screening including records
        """
        try:
            # Get the bulk screening record
            try:
                # Filter by user unless admin
                if request.user.is_staff:
                    bulk_screening = BulkAmlScreening.objects.get(id=bulk_id)
                else:
                    bulk_screening = BulkAmlScreening.objects.get(id=bulk_id, user=request.user)
            except BulkAmlScreening.DoesNotExist:
                return Response({"error": "Bulk AML screening not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get page and limit parameters for records pagination
            try:
                page = int(request.query_params.get('page', 1))
            except (TypeError, ValueError):
                page = 1
                
            try:
                page_size = int(request.query_params.get('limit', 20))
                # Cap page size to reasonable limits
                page_size = min(max(page_size, 1), 100)  # Between 1 and 100
            except (TypeError, ValueError):
                page_size = 20
            
            # Get records with pagination
            records_queryset = BulkAmlScreeningRecord.objects.filter(bulk_screening=bulk_screening).order_by('id')
            
            # Apply pagination
            paginator = PageNumberPagination()
            paginator.page_size = page_size
            paginated_records = paginator.paginate_queryset(records_queryset, request)
            
            # Format records data
            records_data = []
            for record in paginated_records:
                # Get verification details if available
                verification_info = None
                if record.verification_id:
                    try:
                        verification = Verification.objects.get(id=record.verification_id)
                        verification_info = {
                            "id": verification.id,
                            "reference_id": verification.reference_id,
                            "status": verification.status,
                            "created_at": verification.created_at
                        }
                    except Verification.DoesNotExist:
                        pass
                
                # Format countries for display
                countries_data = []
                if record.countries and isinstance(record.countries, list):
                    countries_data = record.countries
                
                records_data.append({
                    "id": record.id,
                    "full_name": record.full_name,
                    "date_of_birth": record.date_of_birth,
                    "countries": countries_data,
                    "screening_models": record.screening_models,
                    "is_manual_review": record.is_manual_review,
                    "decline_on_single_step": record.decline_on_single_step,
                    "check_family": record.check_family,
                    "status": record.status,
                    "verification": verification_info,
                    "error_message": record.error_message,
                    "created_at": record.created_at
                })
            
            # Get bulk screening data
            bulk_data = {
                "id": bulk_screening.id,
                "reference_id": bulk_screening.reference_id,
                "file_name": bulk_screening.file_name,
                "total_records": bulk_screening.total_records,
                "processed_records": bulk_screening.processed_records,
                "status": bulk_screening.status,  # Use actual status from model
                "error_message": bulk_screening.error_message,
                "created_at": bulk_screening.created_at,
                "updated_at": bulk_screening.updated_at
            }
            
            return Response({
                "message": "Details retrieved successfully",
                "data": {
                    "bulk_screening": bulk_data,
                    "records": records_data,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": records_queryset.count()
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
