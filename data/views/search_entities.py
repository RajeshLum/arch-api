import operator
from functools import reduce
from typing import List, Any, Dict
from datetime import datetime, date
from decimal import Decimal

from django.apps import apps
from django.db.models import Model, Q
from django.db.models.functions import Cast
from django.db.models import CharField
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import *
from ..amlmodels.verification_models import Verification
from ..amlmodels.verification_metadata_models import VerificationInfo
from ..amlmodels.verification_timeline_models import VerificationTimeline


class SearchEntitiesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Search entities across models",
        description="Performs a case-insensitive search across text fields of entity models. Results are sorted by relevance score.",
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search query string",
                required=True,
                type=str,
                examples=[
                    OpenApiExample(
                        "Example Query",
                        value="example search"
                    ),
                ]
            ),
            OpenApiParameter(
                name="limit",
                description="Maximum number of results to return",
                required=False,
                type=int,
                default=10,
            ),
            OpenApiParameter(
                name="entity_type",
                description="Filter results by specific entity type (model name)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="country",
                description="Filter results by country",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="topics",
                description="Filter results by topics",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "example": 10
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "relevance": {"type": "number"},
                                "attributes": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        }
                    }
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "The 'q' parameter is required."
                    }
                }
            }
        },
        tags=["Sanction Query"]
    )
    
    def get(self, request, *args, **kwargs):
        limit = int(request.query_params.get("limit", 10))
        verification_id = request.query_params.get("verification_id")
        
        query_string = request.query_params.get("q", "").strip()
        countries = [c.lower() for c in request.query_params.getlist("countries[]")]
        entity_types = request.query_params.getlist("entity_types[]")
        registration_number = request.query_params.get("registration_number")
        check_family = request.query_params.get("check_family")

        if not query_string:
            return Response(
                {"error": "The 'q' parameter is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        app_config = apps.get_app_config("data")
        models = [
            m for m in app_config.get_models()
            if m.__module__ == "data.models" 
            and m.__name__ != "BatchUpload" and m.__name__ != "BatchError"
            and (check_family == "true" or m.__name__ != "Family")
        ]
        
        if entity_types:
            try:
                models = [
                    apps.get_model(app_label="data", model_name=et)
                    for et in entity_types
                ]
            except LookupError as e:
                return Response(
                    {"error": f"Model not found: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        results = []
        screening_models = []
        
        # Create VerificationTimeline entry if verification_id is provided
        if verification_id:
            try:
                verification = Verification.objects.get(id=verification_id)
                # Create first timeline entry for search performed
                VerificationTimeline.objects.create(
                    verification=verification,
                    status='pending',
                    action='search_performed',
                    notes=f'Search performed with query: {query_string}',
                    performed_by=request.user
                )
            except Verification.DoesNotExist:
                # If verification doesn't exist, just continue without creating timeline entry
                pass
            except Exception as e:
                # Log the error but don't interrupt the response
                print(f"Error creating verification timeline or info: {str(e)}")

        for model in models:
            try:
                # print(f"Looping model: {model.__name__}")
                screening_models.append(model.__name__)

                # Only search 'name' field if it exists
                if any(field.name == 'name' for field in model._meta.fields):
                    search_fields = [Q(name__contains=[query_string])]
                else:
                    continue  # Skip models without a 'name' field

                filters = []
                if countries:
                    country_q = []
                    if any(field.name == 'country' for field in model._meta.fields):
                        country_q.extend([Q(country__contains=[c]) for c in countries])
                    if any(field.name == 'countryName' for field in model._meta.fields):
                        country_q.extend([Q(countryName__icontains=c) for c in countries])
                    if country_q:
                        filters.append(reduce(operator.or_, country_q))

                if registration_number:
                    # Cast registrationNumber to string for comparison
                    filters.append(Q(**{'registrationNumber__icontains': str(registration_number)}) | Q(**{'registrationNumber__isnull': False}) & Q(**{'registrationNumber__in': [registration_number, str(registration_number)]}))

                combined_query = reduce(operator.or_, search_fields)
         
                if filters:
                    combined_query &= reduce(operator.and_, filters)

                query_results = model.objects.filter(combined_query)[:limit]

                for result in query_results:
                    relevance_score = self.calculate_relevance(query_string, result)
                    # Create a serializable dictionary of attributes
                    attributes = {}
                    for field in result._meta.fields:
                        try:
                            field_value = getattr(result, field.name)
                            attributes[field.name] = self.serialize_field(field_value)
                        except Exception as e:
                            attributes[field.name] = f"Error serializing: {str(e)}"
                    
                    
                    results.append({
                        "id": result.id,
                        "name": str(result),
                        "relevance": relevance_score,
                        "attributes": attributes,
                        "model_type": result._meta.model_name
                    })

            except Exception as e:
                continue  

        results = sorted(results, key=lambda x: x["relevance"], reverse=True)

        # If results are found, update verification note if verification_id is provided
        if results and verification_id:
            try:
                verification_obj = Verification.objects.get(id=verification_id)
                verification_obj.note = 'Verification information found in Sanction entity'
                verification_obj.save(update_fields=["note"])
            except Verification.DoesNotExist:
                pass
            except Exception as e:
                print(f"Error updating verification note: {str(e)}")

        # If no results, create a customer from q and dob, but do not return the customer in results
        if not results:
            from data.models import Customer
            from data.serializers.customer import CustomerSerializer
            q = query_string
            dob = request.query_params.get("dob")
            names = q.split()
            first_name = names[0] if names else ""
            last_name = " ".join(names[1:]) if len(names) > 1 else ""
            customer_data = {
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob,
                "registration_number": registration_number,
                "user": request.user.id,
                "status": "verified",
                "verification_id": verification_id
            }
            
            # Remove dob if not provided
            if not dob:
                customer_data.pop("dob")
            serializer = CustomerSerializer(data=customer_data)
            
            if serializer.is_valid():
                customer_instance = serializer.save(user=request.user)
                results = []  # Do not return the new customer
                # Update Verification.customer_id if verification_id is provided
                if verification_id:
                    try:
                        verification_obj = Verification.objects.get(id=verification_id)
                        verification_obj.customer_id = customer_instance.id
                        # Update verification status to verified when no results are found
                        verification_obj.status = "verified"
                        verification_obj.note = "Verification has been successfully completed."
                        verification_obj.save(update_fields=["customer_id", "status", "note"])
                    except Verification.DoesNotExist:
                        pass
            else:
                return Response({"error": "Customer creation failed", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create second timeline entry based on search results
        if verification_id:
            try:
                if results:
                    result_message = 'Verification information found in Sanction entity'
                    result_action = 'sanction_found'
                    timeline_status = 'declined'
                else:
                    result_message = 'No sanction information found. Verification completed successfully.'
                    result_action = 'verification_completed'
                    timeline_status = 'verified'
                    
                VerificationTimeline.objects.create(
                    verification=verification,
                    status=timeline_status,
                    action=result_action,
                    notes=result_message,
                    performed_by=request.user
                )
                
                # --- VerificationInfo integration ---
                is_found = bool(results)
                found_models = []
                for result in results:
                    found_models.append({
                        "model": result.get("model_type"),
                        "id": result.get("id"),
                        "sanction_entity_id": (
                            result["attributes"].get("sanctionEntity", {}).get("id")
                            if "attributes" in result and isinstance(result["attributes"].get("sanctionEntity"), dict)
                            else result["attributes"].get("sanctionId") if "attributes" in result else None
                        )
                    })
                    
                VerificationInfo.objects.create(
                    verification_id=verification_id,
                    screening_models=screening_models,
                    is_found=is_found,
                    found_models=found_models
                )
                # --- End VerificationInfo integration ---
            except Verification.DoesNotExist:
                # If verification doesn't exist, just continue without creating timeline entry
                pass
            except Exception as e:
                # Log the error but don't interrupt the response
                print(f"Error creating verification timeline or info: {str(e)}")

        return Response({"limit": limit, "results": results}, status=status.HTTP_200_OK)

    def calculate_relevance(self, query, result):
        """
        Calculate relevance based on how well the result matches the query.
        """
        match_count = sum(
            1 for field in result._meta.fields 
            if field.get_internal_type() in ["CharField", "TextField"] and 
               query.lower() in str(getattr(result, field.name)).lower()
        )
        total_fields = sum(
            1 for field in result._meta.fields if field.get_internal_type() in ["CharField", "TextField"]
        )
        return round(match_count / total_fields, 2) if total_fields else 0.0

    def serialize_field(self, value: Any) -> Any:
        """Recursively serialize a value to ensure it's JSON serializable"""
        try:
            # Handle None
            if value is None:
                return None
                
            # Handle basic JSON-serializable types
            if isinstance(value, (str, int, float, bool)):
                return value
                
            # Handle decimal values
            if isinstance(value, Decimal):
                return float(value)
                
            # Handle date and datetime objects
            if isinstance(value, (datetime, date)):
                return value.isoformat()
                
            # Handle Django model instances
            if isinstance(value, Model):
                return {
                    'id': value.id if hasattr(value, 'id') else None,
                    'type': value.__class__.__name__,
                    'str_representation': str(value)
                }
                
            # Handle lists and tuples recursively
            if isinstance(value, (list, tuple)):
                return [self.serialize_field(item) for item in value]
                
            # Handle dictionaries recursively
            if isinstance(value, dict):
                return {k: self.serialize_field(v) for k, v in value.items()}
                
            # Handle sets by converting to list first
            if isinstance(value, set):
                return [self.serialize_field(item) for item in value]
                
            # Handle objects with __dict__ attribute (custom classes)
            if hasattr(value, '__dict__'):
                # Convert to dict and recursively serialize each attribute
                obj_dict = {}
                for k, v in value.__dict__.items():
                    # Skip private attributes and callables
                    if not k.startswith('_') and not callable(v):
                        try:
                            obj_dict[k] = self.serialize_field(v)
                        except:
                            obj_dict[k] = str(v)
                return obj_dict
                
            # For any other type, convert to string
            return str(value)
            
        except Exception as e:
            # Return a string representation as fallback
            return f"Serialization error: {str(e)}"