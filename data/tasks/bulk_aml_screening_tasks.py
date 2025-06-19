import os
import csv
import json
import pandas as pd
from io import StringIO
from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from data.amlmodels.bulk_aml_screening_models import BulkAmlScreening, BulkAmlScreeningRecord
from data.amlmodels.verification_models import Verification
from data.amlmodels.verification_metadata_models import VerificationInfo
from data.amlmodels.verification_timeline_models import VerificationTimeline
from data.utils.reference_generator import generate_reference_id
from data.utils.geolocation import get_user_country
from data.views.search_entities import SearchEntitiesView
from rest_framework.test import APIRequestFactory
from data.views.verification.verify_document import VerificationListCreateView


def process_bulk_aml_screening(bulk_screening_id, request):
    """
    Process a bulk AML screening file
    This would typically be a Celery task in production
    """
    try:
        # Get the bulk screening record
        bulk_screening = BulkAmlScreening.objects.get(id=bulk_screening_id)
        
        # Update status to processing
        bulk_screening.status = 'processing'
        bulk_screening.save()
        
        # Get file path and extension
        file_path = bulk_screening.file_path
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Read the file
        records = []
        try:
            if file_extension == '.csv':
                with default_storage.open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(row)
            else:  # Excel file
                file_content = default_storage.open(file_path, 'rb').read()
                df = pd.read_excel(file_content)
                records = df.to_dict('records')
        except Exception as e:
            bulk_screening.status = 'failed'
            bulk_screening.error_message = f"Error reading file: {str(e)}"
            bulk_screening.save()
            return
        
        # Parse countries and models from request
        countries = request.data.get('countries', '[]')
        screening_models = request.data.get('screening_models', '[]')
        
        # Parse additional options
        is_manual_review = request.data.get('is_manual_review', 'false').lower() in ['true', 'yes', '1']
        decline_on_single_step = request.data.get('decline_on_single_step', 'false').lower() in ['true', 'yes', '1']
        check_family = request.data.get('check_family', 'false').lower() in ['true', 'yes', '1']
            
        # Process each record
        processed_records = 0
        
        # Create a search view instance for reuse
        search_view = SearchEntitiesView()
        
        # Process records in batches to avoid memory issues
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch_records = records[i:i+batch_size]
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                for record in batch_records:
                    try:
                        # Extract data from record
                        full_name = record.get('full_name', '')
                        if not full_name:
                            # Try alternative field names
                            full_name = record.get('name', '') or record.get('fullname', '')
                        
                        if not full_name:
                            continue  # Skip records without a name
                        
                        # Parse date of birth
                        date_of_birth = None
                        dob_str = record.get('date_of_birth', '') or record.get('dob', '')
                        if dob_str:
                            try:
                                # Try different date formats
                                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                                    try:
                                        date_of_birth = datetime.strptime(dob_str, fmt).date()
                                        break
                                    except:
                                        continue
                            except:
                                pass
                        
                        # Get country and convert to list for countries field
                        country = record.get('country', '')
                        countries_list = [country] if country else []
                        
                        # Create bulk screening record with form data
                        record_data = {
                            "full_name": full_name,
                            "date_of_birth": date_of_birth,
                            "countries": countries,
                            "screening_models": screening_models,
                            "is_manual_review": is_manual_review,
                            "decline_on_single_step": decline_on_single_step,
                            "check_family": check_family,
                            "status": "pending"
                        }

                        aml_record = BulkAmlScreeningRecord.objects.create(
                            bulk_screening=bulk_screening,
                            **record_data
                        )
                        
                        verify_data = {
                            **record_data,
                            "service_id": 1,
                            "bulk_aml_record_id": aml_record.id
                        }
                        
                        # Call VerificationListCreateView.post as internal API
                        factory = APIRequestFactory()
                        request_api = factory.post('/api/verification/', verify_data, format='json')
                        request_api.user = bulk_screening.user
                        request_api._force_auth_user = bulk_screening.user
                        request_api._authenticated = True
                        view = VerificationListCreateView.as_view()
                        response = view(request_api)
                        # Optionally, handle response.data or errors
                        
                        verification_id = response.data.get('id')
                        search_data = {
                            **verify_data,
                            "q": full_name
                        }
                        if verification_id is not None:
                            search_data["verification_id"] = verification_id

                        # --- Call SearchEntitiesView.get as internal API ---
                        if verification_id is not None:
                            factory_search = APIRequestFactory()
                            request_search = factory_search.get('/api/search-entities/', search_data)
                            request_search.user = bulk_screening.user
                            request_search._force_auth_user = bulk_screening.user
                            request_search._authenticated = True
                            search_view = SearchEntitiesView.as_view()
                            search_response = search_view(request_search)
                            print('search_response>>>')
                            print(search_response)
                        # --- End internal API call ---

                        # Record processing completed
                        processed_records += 1
                        
                    except Exception as e:
                        # Log error and continue with next record
                        print(f"Error processing record {record.get('full_name', 'Unknown')}: {str(e)}")
                        
            # Update bulk screening progress after each batch
            bulk_screening.processed_records = processed_records
            bulk_screening.save()
        
        # No result file to save
        
        # Update bulk screening record with processed records and set status to completed
        bulk_screening.processed_records = processed_records
        bulk_screening.status = 'completed'
        bulk_screening.save()
        
    except Exception as e:
        # Update bulk screening record with error
        try:
            bulk_screening = BulkAmlScreening.objects.get(id=bulk_screening_id)
            bulk_screening.error_message = str(e)
            bulk_screening.status = 'failed'
            bulk_screening.save()
        except:
            pass
        
        print(f"Error processing bulk AML screening {bulk_screening_id}: {str(e)}")
