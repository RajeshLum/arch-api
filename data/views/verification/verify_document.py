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
from django.contrib.auth import get_user_model
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
        service_id = request.query_params.get('service_id')
        filter_status = request.query_params.get('status')
        if request.user.is_staff:
            queryset = Verification.objects.all().order_by('-created_at')
        else:
            queryset = Verification.objects.filter(user=request.user).order_by('-created_at')

        # Filter by service_id if provided
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        if filter_status:
            queryset = queryset.filter(status=filter_status)
            
        # Get dynamic page and limit parameters from request
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

        # Apply pagination manually with dynamic page size
        paginator = PageNumberPagination()
        paginator.page_size = page_size
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
                        customer_info = f"{customer.first_name} {customer.last_name}".strip()
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
                'is_manual_review': verification.is_manual_review,
                'document': verification.document,
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

        import csv
        from io import StringIO
        from data.amlmodels.template_models import TemplateTitle
        file_paths = []
        template_id = request.data.get('template_id')
        service_id = int(request.data.get('service_id', 1))
        document_rows = []
        for file in files:
            filename = f'{uuid.uuid4()}_{file.name}'
            if template_id:
                path = default_storage.save(f'uploads/document/verifications/investors/template/{template_id}/{filename}', ContentFile(file.read()))
            else:
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
        
        import json
        # Ensure template_answers is always a dict
        template_answers = request.data.get('template_answers', {})
        if isinstance(template_answers, str):
            try:
                template_answers = json.loads(template_answers)
            except Exception:
                template_answers = {}

        data = {
            'user': request.user.id,
            'reference_id': reference_id,
            'template_id': request.data.get('template_id', 0),
            'template_answers': template_answers,
            'customer_id': request.data.get('customer_id', ''),
            'id_type': request.data.get('id_type', ''),
            'country_id': request.data.get('country_id', country_code),  # Use provided country or auto-detect
            'service_id': request.data.get('service_id', 1),
            'document': request.data.get('document_path', file_paths),
            'status': 'declined',
            'note': 'Verification process started.',
            'is_manual_review': is_manual_review,
        }
            
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            verification = serializer.save(user=request.user)

            # Bulk AML integration: update BulkAmlScreeningRecord if bulk_aml_record_id is present
            bulk_aml_record_id = request.data.get('bulk_aml_record_id')
            if bulk_aml_record_id:
                try:
                    from data.amlmodels.bulk_aml_screening_models import BulkAmlScreeningRecord
                    record = BulkAmlScreeningRecord.objects.get(id=bulk_aml_record_id)
                    record.verification_id = verification.id
                    record.status = 'completed'
                    record.save(update_fields=['verification_id', 'status', 'updated_at'])
                except Exception as e:
                    print(f"Error updating BulkAmlScreeningRecord: {e}")
            
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
            
            # If service_id == 4, parse the CSV
            if service_id == 4 and files:
                file.seek(0)
                csv_text = file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(csv_text), fieldnames=["Page Title","Questions","Answer Type","Options"])
                document_rows = list(reader)

            # If service_id == 4, fetch template info from DB and match questions
            matched_questions = []
            all_matched = True
            if service_id == 4 and template_id and files:
                try:
                    template_obj = TemplateTitle.objects.prefetch_related('pages__questions').get(pk=template_id, user=request.user)
                    # Build a lookup for document questions
                    doc_question_map = {row['Questions']: row for row in document_rows}
                    total_questions = 0
                    matched_count = 0
                    for page in template_obj.pages.all():
                        for q in page.questions.all():
                            total_questions += 1
                            q_title = q.question
                            doc_row = doc_question_map.get(q_title)
                            if doc_row:
                                matched_count += 1
                                matched_questions.append({
                                    'template_question': {
                                        'id': q.id,
                                        'question': q.question,
                                        'description': q.description,
                                        'answer_type': q.answer_type,
                                        'required': q.required,
                                        'options': q.options,
                                        'description_enabled': q.description_enabled
                                    },
                                    'document_row': doc_row,
                                    'page_title': page.page_title
                                })
                            else:
                                matched_questions.append({
                                    'template_question': {
                                        'id': q.id,
                                        'question': q.question,
                                        'description': q.description,
                                        'answer_type': q.answer_type,
                                        'required': q.required,
                                        'options': q.options,
                                        'description_enabled': q.description_enabled
                                    },
                                    'document_row': None,
                                    'page_title': page.page_title
                                })
                    
                    all_matched = (matched_count == total_questions and total_questions > 0)
                    if not all_matched:
                        verification.status = 'declined'
                        verification.save(update_fields=['status'])
                        VerificationTimeline.objects.create(
                            verification=verification,
                            status='declined',
                            action='declined',
                            notes='Verification declined due to unmatched template questions',
                            performed_by=request.user
                        )
                except Exception as e:
                    # Log or handle the error as needed
                    print(f"Error fetching or matching template info: {e}")
            
            if service_id == 4:
                response_data = dict(serializer.data)
                response_data['all_matched'] = all_matched
                if not all_matched:
                    response_data['status'] = 'declined'
                    response_data['msg'] = 'Verification declined due to unmatched template questions'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
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

        # Get verification_info if it exists
        from data.amlmodels.verification_metadata_models import VerificationInfo
        try:
            verification_info = VerificationInfo.objects.get(verification_id=verification.id)
            found_models_with_extra = []
            from data.models import SanctionedEntity
            from data.serializers.entity_details import EntityDetailSerializer
            from django.apps import apps
            from django.forms.models import model_to_dict
            from collections import defaultdict

            # Step 1: Collect ids by model name
            model_id_map = defaultdict(set)
            for fm in verification_info.found_models or []:
                model_name = fm.get('model')
                entity_id = fm.get('id')
                if model_name and entity_id:
                    model_id_map[model_name.lower()].add(entity_id)

            # Step 2: Bulk fetch all needed instances
            model_instance_map = {}
            for model_name, ids in model_id_map.items():
                ModelClass = None
                for m in apps.get_app_config('data').get_models():
                    if m.__name__.lower() == model_name:
                        ModelClass = m
                        break
                if ModelClass:
                    instances = ModelClass.objects.filter(id__in=ids)
                    for instance in instances:
                        model_instance_map[(model_name, instance.id)] = instance

            # Helper to recursively remove keys with None values
            def remove_nulls(obj):
                if isinstance(obj, dict):
                    return {k: remove_nulls(v) for k, v in obj.items() if v is not None}
                elif isinstance(obj, list):
                    return [remove_nulls(v) for v in obj if v is not None]
                else:
                    return obj

            for fm in verification_info.found_models or []:
                fm_copy = dict(fm)
                extra = {}
                # Add SanctionedEntity details if sanction_entity_id exists
                sanction_entity_id = fm.get('sanction_entity_id')
                if sanction_entity_id:
                    try:
                        sanctioned_entity = SanctionedEntity.objects.get(id=sanction_entity_id)
                        sanctioned_entity_data = EntityDetailSerializer(sanctioned_entity).to_dict()
                        if sanctioned_entity_data is not None:
                            cleaned = remove_nulls(sanctioned_entity_data)
                            if 'linkedEntities' in cleaned:
                                del cleaned['linkedEntities']
                            extra['sanctioned_entity'] = cleaned
                    except SanctionedEntity.DoesNotExist:
                        pass  # Do not add null
                # Add related model details using model name (schema) and id using pre-fetched map
                model_name = fm.get('model')
                entity_id = fm.get('id')
                if model_name and entity_id:
                    instance = model_instance_map.get((model_name.lower(), entity_id))
                    if instance is not None:
                        extra['entity'] = remove_nulls(model_to_dict(instance))
                fm_copy['extra'] = extra
                found_models_with_extra.append(fm_copy)

            verification_data['verification_info'] = {
                'id': verification_info.id,
                'verification_id': verification_info.verification_id,
                'screening_models': verification_info.screening_models,
                'is_found': verification_info.is_found,
                'found_models': found_models_with_extra,
                'created_at': verification_info.created_at,
                'updated_at': verification_info.updated_at,
            }
        except VerificationInfo.DoesNotExist:
            verification_data['verification_info'] = None

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
