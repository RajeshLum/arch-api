import os
import re
from pprint import pprint

import cv2
import pytesseract
from django.db.models import Q
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

    def post(self, request):
        """Handle passport image upload and return extracted data with matching person"""
        serializer = PassportImageSerializer(data=request.data)
        
        if serializer.is_valid():
            image = request.FILES['image']
            image_path = "/tmp/" + image.name  
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Extract passport information
            passport_info = extract_passport_info(image_path)
            
            # Find matching person using MRZ data
            matching_person = None
            if passport_info['MRZ Data']:
                matching_person = find_matching_person(passport_info['MRZ Data'])
            
            # Add matching person to response if found
            response_data = passport_info
            if matching_person:
                response_data['matching_person'] = PersonSerializer(matching_person).data
                response_data['match_confidence'] = calculate_person_match_score(
                    matching_person, 
                    passport_info['MRZ Data']
                )
            
            os.remove(image_path)
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)