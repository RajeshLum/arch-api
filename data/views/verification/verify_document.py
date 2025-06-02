import uuid
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from data.models import Verification
from data.serializers.verification import VerificationSerializer
from data.utils.geolocation import get_user_country

# list, add
class VerificationListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get1(self, request):
        """List all verification for the authenticated user (admin gets all)"""
        if request.user.is_staff:
            verifications = Verification.objects.all()
        else:
            verifications = Verification.objects.filter(user=request.user)
        
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        if request.user.is_staff:
            queryset = Verification.objects.all().order_by('-id')
        else:
            queryset = Verification.objects.filter(user=request.user).order_by('-id')

        # Apply pagination manually
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = VerificationSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """Create a new verification for the authenticated user"""
        data = request.data.copy()
        data['user'] = request.user.id
        
        files = request.FILES.getlist('document')

        file_paths = []
        for file in files:
            filename = f'{uuid.uuid4()}_{file.name}'
            path = default_storage.save(f'uploads/document/verifications/{filename}', ContentFile(file.read()))
            file_paths.append(path)

        # Get user's country code from IP or header
        country_code = get_user_country(request)
        
        data = {
            'user': request.user.id,
            'customer_id': request.data.get('customer_id', ''),
            'id_type': request.data.get('id_type', ''),
            'country_id': request.data.get('country_id', country_code),  # Use provided country or auto-detect
            'service_id': request.data.get('service_id', 1),
            'document': file_paths,
            'status': 'pending',
        }
            
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_verification(self, pk, user):
        """Helper to get object ensuring user access"""
        if user.is_staff:
            return get_object_or_404(Verification, pk=pk)
        
        return get_object_or_404(Verification, pk=pk, user=user)

    def get(self, request, pk):
        """Retrieve a specific verification"""
        verification = self.get_verification(pk, request.user)
        serializer = VerificationSerializer(verification)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update a specific verification (partial update)"""
        verification = self.get_verification(pk, request.user)
        
        # Get user's country code from IP or header if not already provided
        country_code = get_user_country(request)
        
        update_data = {
            'customer_id': request.data.get('customer_id', verification.customer_id),
            'id_type': request.data.get('id_type', verification.id_type),
            'country_id': request.data.get('country_id', verification.country_id or country_code),
            'service_id': request.data.get('service_id', verification.service_id),
            'status': request.data.get('status', verification.status),
        }

        files = request.FILES.getlist('document')
        file_paths = []
        
        if files:
            for file in files:
                # filename = f'{uuid.uuid4()}_{file.name}'
                # filename = f'_{file.name}'
                
                uuid_str = str(uuid.uuid4())
                short_uuid = uuid_str[:16]
                filename = f'{short_uuid}_{file.name}'
                
                path = default_storage.save(f'uploads/document/verifications/{filename}', ContentFile(file.read()))
                file_paths.append(path)

            # Append new files to existing document list
            if isinstance(verification.document, list):
                update_data['document'] = verification.document + file_paths
            else:
                update_data['document'] = file_paths  # fallback if somehow not a list
        else:
            update_data['document'] = verification.document
        
        serializer = VerificationSerializer(verification, data=update_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a verification"""
        verification = self.get_verification(pk, request.user)
        verification.delete()
        
        return Response({"detail": "Verification deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
