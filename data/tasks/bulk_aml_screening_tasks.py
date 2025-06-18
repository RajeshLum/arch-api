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


def process_bulk_aml_screening(bulk_screening_id):
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
        
        # Process each record
        processed_records = 0
        matched_records = 0
        
        # Parse countries and models
        countries = bulk_screening.countries
        if isinstance(countries, str):
            try:
                countries = json.loads(countries)
            except:
                countries = []
                
        screening_models = bulk_screening.screening_models
        if isinstance(screening_models, str):
            try:
                screening_models = json.loads(screening_models)
            except:
                screening_models = []
        
        # Create a search view instance for reuse
        search_view = SearchEntitiesView()
        
        # Create result file
        result_file_path = f'uploads/bulk_aml_screening/results/{bulk_screening.reference_id}_results.csv'
        result_file = StringIO()
        result_writer = csv.writer(result_file)
        
        # Write header
        result_writer.writerow([
            'Full Name', 'Date of Birth', 'Country', 'Status', 
            'Verification ID', 'Matched Entities', 'Error Message'
        ])
        
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
                        
                        # Get country
                        country = record.get('country', '')
                        
                        # Create bulk screening record
                        aml_record = BulkAmlScreeningRecord.objects.create(
                            bulk_screening=bulk_screening,
                            full_name=full_name,
                            date_of_birth=date_of_birth,
                            country=country,
                            status='processing'
                        )
                        
                        # Generate a unique reference ID for the verification
                        reference_id = generate_reference_id()
                        
                        # Create verification record - similar to VerificationListCreateView.post
                        verification = Verification.objects.create(
                            user=bulk_screening.user,
                            full_name=full_name,
                            date_of_birth=date_of_birth,
                            country_id=country,
                            is_manual_review=bulk_screening.is_manual_review,
                            decline_on_single_step=bulk_screening.decline_on_single_step,
                            check_family=bulk_screening.check_family,
                            status='processing',
                            reference_id=reference_id,
                            source='bulk_aml_screening',
                            source_reference=f"{bulk_screening.reference_id}:{aml_record.id}"
                        )
                        
                        # Create verification timeline entry
                        VerificationTimeline.objects.create(
                            verification=verification,
                            status='processing',
                            action='created',
                            notes=f'Created from bulk AML screening {bulk_screening.reference_id}',
                            performed_by=bulk_screening.user
                        )
                        
                        # Update AML record with verification ID
                        aml_record.verification_id = verification.id
                        aml_record.save()
                        
                        # Create a mock request class for the search view
                        class MockRequest:
                            def __init__(self, user, query_params):
                                self.user = user
                                self.query_params = query_params
                            
                            def get(self, key, default=None):
                                return self.query_params.get(key, default)
                            
                            def getlist(self, key):
                                val = self.query_params.get(key)
                                if not isinstance(val, list):
                                    return [val]
                                return val
                        
                        # Build query params - similar to how SearchEntitiesView is called
                        query_params = {
                            'q': full_name,
                            'verification_id': verification.id,
                            'limit': 100
                        }
                        
                        # Add countries if specified
                        if countries:
                            query_params['countries[]'] = [c.get('value') for c in countries if isinstance(c, dict) and 'value' in c]
                        
                        # Add entity types (screening_models) if specified
                        if screening_models:
                            query_params['entity_types[]'] = [m.get('value') for m in screening_models if isinstance(m, dict) and 'value' in m]
                        
                        # Add DOB if available
                        if date_of_birth:
                            query_params['dob'] = date_of_birth.strftime('%Y-%m-%d')
                        
                        # Create mock request
                        mock_request = MockRequest(bulk_screening.user, query_params)
                        
                        # Call search method - this will create VerificationInfo records automatically
                        try:
                            response = search_view.get(mock_request)
                            
                            # Check if any matches were found
                            results = response.data.get('results', [])
                            
                            if results:
                                aml_record.status = 'matched'
                                aml_record.matched_entities = results
                                matched_records += 1
                                
                                # Update verification status
                                verification.status = 'matched'
                                verification.save()
                                
                                # Add timeline entry for match
                                VerificationTimeline.objects.create(
                                    verification=verification,
                                    status='matched',
                                    action='aml_check',
                                    notes=f'Found {len(results)} potential matches',
                                    performed_by=bulk_screening.user
                                )
                            else:
                                aml_record.status = 'not_matched'
                                
                                # Update verification status
                                verification.status = 'completed'
                                verification.save()
                                
                                # Add timeline entry for no match
                                VerificationTimeline.objects.create(
                                    verification=verification,
                                    status='completed',
                                    action='aml_check',
                                    notes='No matches found',
                                    performed_by=bulk_screening.user
                                )
                            
                            aml_record.save()
                            
                        except Exception as e:
                            aml_record.status = 'error'
                            aml_record.error_message = str(e)
                            aml_record.save()
                            
                            # Update verification status
                            verification.status = 'error'
                            verification.save()
                            
                            # Add timeline entry for error
                            VerificationTimeline.objects.create(
                                verification=verification,
                                status='error',
                                action='aml_check',
                                notes=f'Error during screening: {str(e)}',
                                performed_by=bulk_screening.user
                            )
                        
                        # Write to result file
                        result_writer.writerow([
                            full_name,
                            date_of_birth.strftime('%Y-%m-%d') if date_of_birth else '',
                            country,
                            aml_record.status,
                            verification.id,
                            len(results) if 'results' in locals() else 0,
                            aml_record.error_message or ''
                        ])
                        
                        processed_records += 1
                        
                    except Exception as e:
                        # Log error and continue with next record
                        print(f"Error processing record {record.get('full_name', 'Unknown')}: {str(e)}")
                        
                        # Create error record
                        BulkAmlScreeningRecord.objects.create(
                            bulk_screening=bulk_screening,
                            full_name=record.get('full_name', 'Unknown'),
                            status='error',
                            error_message=str(e)
                        )
            
            # Update bulk screening progress after each batch
            bulk_screening.processed_records = processed_records
            bulk_screening.matched_records = matched_records
            bulk_screening.save()
        
        # Save result file
        default_storage.save(result_file_path, ContentFile(result_file.getvalue()))
        
        # Update bulk screening record
        bulk_screening.processed_records = processed_records
        bulk_screening.matched_records = matched_records
        bulk_screening.status = 'completed'
        bulk_screening.result_file_path = result_file_path
        bulk_screening.save()
        
    except Exception as e:
        # Update bulk screening record with error
        try:
            bulk_screening = BulkAmlScreening.objects.get(id=bulk_screening_id)
            bulk_screening.status = 'failed'
            bulk_screening.error_message = str(e)
            bulk_screening.save()
        except:
            pass
        
        print(f"Error processing bulk AML screening {bulk_screening_id}: {str(e)}")
