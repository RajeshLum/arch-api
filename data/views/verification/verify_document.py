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
from data.amlmodels.verification_metadata_models import VerificationMetadata
from data.amlmodels.verification_timeline_models import VerificationTimeline
from data.amlmodels.customer_models import Customer
from data.amlmodels.aml_services_models import AmlService
from data.serializers.verification import VerificationSerializer
from data.serializers.verification_metadata import VerificationMetadataSerializer
from data.serializers.verification_timeline import VerificationTimelineSerializer
from data.utils.geolocation import get_user_country, get_client_ip
from data.utils.reference_generator import generate_reference_id
from data.utils.user_agent_parser import parse_user_agent

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
        
        # Format paginated verifications data with service_name and customer info
        verifications_data = []
        for verification in paginated_qs:
            # Get customer info as a string
            customer_info = ""
            if verification.customer_id:
                try:
                    customer = Customer.objects.filter(id=verification.customer_id).first()
                    if customer:
                        customer_info = f"{customer.first_name} {customer.last_name} ({customer.email})".strip()
                except Exception:
                    pass
            
            # Get service name if service_id is available
            service_name = ""
            if verification.service_id:
                try:
                    service = AmlService.objects.filter(id=verification.service_id).first()
                    if service:
                        service_name = service.service_name
                except Exception:
                    pass
            
            verifications_data.append({
                'id': verification.id,
                'reference_id': verification.reference_id or '',
                'country': verification.country_id or '',
                'customer_id': verification.customer_id,
                'info': customer_info,
                'id_type': verification.id_type,
                'service_id': verification.service_id,
                'service_name': service_name,
                'status': verification.status,
                'created_at': verification.created_at.isoformat(),
                'updated_at': verification.updated_at.isoformat()
            })
        
        # Create custom paginated response
        response = {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': verifications_data
        }
        
        return Response(response)
    
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
        
        # Generate a unique reference ID
        reference_id = generate_reference_id(16)
        
        # Determine if manual review is required
        is_manual_review = request.data.get('is_manual_review', False)
        if isinstance(is_manual_review, str):
            is_manual_review = is_manual_review.lower() in ['true', 'yes', '1']
        
        data = {
            'user': request.user.id,
            'reference_id': reference_id,
            'customer_id': request.data.get('customer_id', ''),
            'id_type': request.data.get('id_type', ''),
            'country_id': request.data.get('country_id', country_code),  # Use provided country or auto-detect
            'service_id': request.data.get('service_id', 1),
            'document': file_paths,
            'status': 'pending',
            'is_manual_review': is_manual_review,
        }
            
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            verification = serializer.save(user=request.user)
            
            # Store user IP and browser information
            ip_address = get_client_ip(request)
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent_data = parse_user_agent(user_agent_string)
            
            # Create metadata record
            VerificationMetadata.objects.create(
                verification=verification,
                ip_address=ip_address,
                user_agent=user_agent_string,
                browser=user_agent_data['browser'],
                browser_version=user_agent_data['browser_version'],
                os=user_agent_data['os'],
                device=user_agent_data['device']
            )
            
            # Create initial timeline entry
            VerificationTimeline.objects.create(
                verification=verification,
                status='pending',
                action='created',
                notes='Verification created with pending status',
                performed_by=request.user
            )
            
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
        """Retrieve a specific verification with its metadata and timeline"""
        verification = self.get_verification(pk, request.user)
        verification_data = VerificationSerializer(verification).data
        
        # Get metadata if it exists
        try:
            metadata = VerificationMetadata.objects.get(verification=verification)
            metadata_serializer = VerificationMetadataSerializer(metadata)
            verification_data['metadata'] = metadata_serializer.data
        except VerificationMetadata.DoesNotExist:
            verification_data['metadata'] = None
        
        # Get timeline entries
        timeline_entries = VerificationTimeline.objects.filter(verification=verification).order_by('-created_at')
        timeline_serializer = VerificationTimelineSerializer(timeline_entries, many=True)
        verification_data['timeline'] = timeline_serializer.data
        
        return Response(verification_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update a specific verification (partial update)"""
        verification = self.get_verification(pk, request.user)
        
        # Get user's country code from IP or header if not already provided
        country_code = get_user_country(request)
        
        # Handle is_manual_review field - convert string values to boolean
        is_manual_review = request.data.get('is_manual_review', verification.is_manual_review)
        if isinstance(is_manual_review, str):
            is_manual_review = is_manual_review.lower() in ['true', 'yes', '1']
        
        update_data = {
            'customer_id': request.data.get('customer_id', verification.customer_id),
            'id_type': request.data.get('id_type', verification.id_type),
            'country_id': request.data.get('country_id', verification.country_id or country_code),
            'service_id': request.data.get('service_id', verification.service_id),
            'status': request.data.get('status', verification.status),
            'is_manual_review': is_manual_review,
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
        
        # Check if status is being updated
        status_changed = 'status' in update_data and update_data['status'] != verification.status
        old_status = verification.status
        
        serializer = VerificationSerializer(verification, data=update_data, partial=True)
        if serializer.is_valid():
            verification = serializer.save()
            
            # Add timeline entry if status changed
            if status_changed:
                VerificationTimeline.objects.create(
                    verification=verification,
                    status=verification.status,
                    action='status_updated',
                    notes=f'Status updated from {old_status} to {verification.status}',
                    performed_by=request.user
                )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a verification"""
        verification = self.get_verification(pk, request.user)
        verification.delete()
        
        return Response({"detail": "Verification deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
