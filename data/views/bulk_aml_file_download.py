import mimetypes
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from data.amlmodels.bulk_aml_screening_models import BulkAmlScreening


@method_decorator(csrf_exempt, name='dispatch')
class BulkAmlScreeningFileDownloadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Download the original file uploaded for bulk AML screening
        """
        try:
            # Get file_id from query parameters
            file_id = request.query_params.get('fileId')
            if not file_id:
                return Response({"error": "File ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the bulk screening record
            try:
                # Get user from token or request
                user = request.user
                
                # Filter by user unless admin
                if user.is_staff:
                    bulk_screening = BulkAmlScreening.objects.get(id=file_id)
                else:
                    bulk_screening = BulkAmlScreening.objects.get(id=file_id, user=user)
            except BulkAmlScreening.DoesNotExist:
                return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if file exists
            if not default_storage.exists(bulk_screening.file_path):
                return Response({"error": "File not found on server"}, status=status.HTTP_404_NOT_FOUND)
            
            # Open the file
            file = default_storage.open(bulk_screening.file_path, 'rb')
            
            # Determine content type based on file extension
            file_name = bulk_screening.file_name
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                # Default to binary stream if type cannot be determined
                content_type = 'application/octet-stream'
            
            # Create response with file
            response = FileResponse(file, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            
            # Add CORS headers to allow browser download
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            
            # Log the download activity
            # You can add activity logging here if needed
            
            return response
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def options(self, request, *args, **kwargs):
        """
        Handle preflight OPTIONS request
        """
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
