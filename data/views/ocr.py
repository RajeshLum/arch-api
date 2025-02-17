import os
import re
from pprint import pprint

import cv2
import pytesseract
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from passporteye import read_mrz
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.serializers.ocr import PassportImageSerializer
from data.utils.ocr_details import extract_passport_info


# DRF API View
class PassportOCRView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get_serializer(self):
        return PassportImageSerializer()
    
    
    
    @extend_schema(
        summary="Handle passport image upload and return extracted data",

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
                description="Passport information extracted successfully.",
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
                name="Successful OCR Extraction",
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
        """Handle passport image upload and return extracted data"""
        serializer = PassportImageSerializer(data=request.data)
        
        if serializer.is_valid():
            image = request.FILES['image']
            image_path = "/tmp/" + image.name  
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Extract passport information
            passport_info = extract_passport_info(image_path)

            os.remove(image_path) 
            return Response(passport_info, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
