import os
import re
from pprint import pprint

import cv2
import pytesseract
# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from fuzzywuzzy import fuzz
from passporteye import read_mrz
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.models import Person
from data.serializers.ocr_aml import PassportImageSerializer, PersonSerializer
from data.utils.ocr import calculate_person_match_score, find_matching_person
from data.views.ocr import extract_passport_info


class PassportOCRLookup(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer(self):
        return PassportImageSerializer()
    
    @extend_schema(
        summary="Handle passport image upload and return extracted data with matching person",

        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Passport image file (JPEG, PNG, etc.)',
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Passport information extracted and matching person found (if applicable).",
                response={
                    "type": "object",
                    "properties": {
                        "Raw OCR Text": {"type": "string", "description": "Raw text extracted from the passport using OCR."},
                        "Parsed Text Data": {
                            "type": "object",
                            "description": "Key passport details parsed from the raw OCR text.",
                            "properties": {
                                "Given Names": {"type": "string", "description": "Given names of the passport holder."},
                                "Surname": {"type": "string", "description": "Surname of the passport holder."},
                                "Passport Number": {"type": "string", "description": "Passport number."},
                                "Nationality": {"type": "string", "description": "Nationality of the passport holder."},
                                "Date of Birth": {"type": "string", "description": "Date of birth of the passport holder."},
                                "Date of Expiry": {"type": "string", "description": "Expiry date of the passport."},
                            },
                        },
                        "MRZ Data": {
                            "type": "object",
                            "description": "Machine Readable Zone (MRZ) data extracted from the passport.",
                            "properties": {
                                "type": {"type": "string", "description": "Type of MRZ (e.g., TD1, TD2, TD3)."},
                                "country": {"type": "string", "description": "Issuing country of the passport."},
                                "number": {"type": "string", "description": "Passport number."},
                                "date_of_birth": {"type": "string", "description": "Date of birth of the passport holder."},
                                "expiration_date": {"type": "string", "description": "Expiry date of the passport."},
                                "nationality": {"type": "string", "description": "Nationality of the passport holder."},
                                "surname": {"type": "string", "description": "Surname of the passport holder."},
                                "given_names": {"type": "string", "description": "Given names of the passport holder."},
                            },
                        },
                        "matching_person": {
                            "type": "object",
                            "description": "Matching person found in the database (if applicable).",
                            "properties": {
                                "id": {"type": "integer", "description": "Unique identifier of the person."},
                                "firstName": {"type": "string", "description": "First name of the person."},
                                "lastName": {"type": "string", "description": "Last name of the person."},
                                "passportNumber": {"type": "string", "description": "Passport number of the person."},
                                "birthDate": {"type": "string", "description": "Date of birth of the person."},
                                "nationality": {"type": "string", "description": "Nationality of the person."},
                            },
                        },
                        "match_confidence": {"type": "number", "description": "Confidence score of the match (0-100)."},
                    }
                }
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response={
                    "type": "object",
                    "properties": {
                        "image": {"type": "array", "items": {"type": "string"}, "description": "Validation errors for the image file."},
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                name="Successful OCR Extraction with Matching Person",
                value={
                    "Raw OCR Text": "Given Names: JOHN\nSurname: DOE\nPassport No.: A12345678\nNationality: USA\nDate of Birth: 21/04/1975\nDate of Expiry: 21/04/2025",
                    "Parsed Text Data": {
                        "Given Names": "JOHN",
                        "Surname": "DOE",
                        "Passport Number": "A12345678",
                        "Nationality": "USA",
                        "Date of Birth": "21/04/1975",
                        "Date of Expiry": "21/04/2025",
                    },
                    "MRZ Data": {
                        "type": "TD3",
                        "country": "USA",
                        "number": "A12345678",
                        "date_of_birth": "750421",
                        "expiration_date": "250421",
                        "nationality": "USA",
                        "surname": "DOE",
                        "given_names": "JOHN",
                    },
                    "matching_person": {
                        "id": 1,
                        "firstName": "JOHN",
                        "lastName": "DOE",
                        "passportNumber": "A12345678",
                        "birthDate": "1975-04-21",
                        "nationality": "USA",
                    },
                    "match_confidence": 95.5,
                },
                status_codes=['200'],
            ),
            OpenApiExample(
                name="Successful OCR Extraction without Matching Person",
                value={
                    "Raw OCR Text": "Given Names: JANE\nSurname: SMITH\nPassport No.: B98765432\nNationality: CAN\nDate of Birth: 15/08/1980\nDate of Expiry: 15/08/2030",
                    "Parsed Text Data": {
                        "Given Names": "JANE",
                        "Surname": "SMITH",
                        "Passport Number": "B98765432",
                        "Nationality": "CAN",
                        "Date of Birth": "15/08/1980",
                        "Date of Expiry": "15/08/2030",
                    },
                    "MRZ Data": {
                        "type": "TD3",
                        "country": "CAN",
                        "number": "B98765432",
                        "date_of_birth": "800815",
                        "expiration_date": "300815",
                        "nationality": "CAN",
                        "surname": "SMITH",
                        "given_names": "JANE",
                    },
                    "matching_person": None,
                    "match_confidence": 0,
                },
                status_codes=['200'],
            ),
            OpenApiExample(
                name="Invalid Image File",
                value={
                    "image": ["No file was submitted."],
                },
                status_codes=['400'],
            ),
        ],
    tags=["OCR"]
    )
    def post(self, request):
        """Handle passport image upload and return extracted data with matching person"""
        serializer = PassportImageSerializer(data=request.data)
        
        if serializer.is_valid():
            image = request.FILES['image']
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('media', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the image to media/uploads folder
            image_path = os.path.join(upload_dir, image.name)
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Determine document type
            doc_type = request.data.get('type')
            if not doc_type:
                return Response({'error': 'Missing required field: type (passport or nid)'}, status=status.HTTP_400_BAD_REQUEST)
            doc_type = doc_type.lower()

            if doc_type == 'passport':
                info = extract_passport_info(image_path)
                # Find matching person using MRZ data
                matching_person = None
                if info['MRZ Data']:
                    matching_person = find_matching_person(info['MRZ Data'])
                response_data = info
                if matching_person:
                    response_data['matching_person'] = PersonSerializer(matching_person).data
                    response_data['match_confidence'] = calculate_person_match_score(
                        matching_person,
                        info['MRZ Data']
                    )
            elif doc_type == 'nid':
                from data.utils.ocr_details import extract_nid_info
                info = extract_nid_info(image_path)
                response_data = info
            elif doc_type == 'driving_license':
                from data.utils.ocr_details import extract_driving_license_info
                info = extract_driving_license_info(image_path)
                response_data = info
            else:
                return Response({'error': 'Invalid type. Supported: passport, nid, driving_license'}, status=status.HTTP_400_BAD_REQUEST)

            # Keep the file in the uploads folder and add the path to the response
            # Ensure image_path uses forward slashes for cross-platform compatibility
            response_data['image_path'] = image_path.replace('\\', '/').replace('\\', '/') if isinstance(image_path, str) else image_path
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)