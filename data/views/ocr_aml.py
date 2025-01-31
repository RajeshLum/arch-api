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
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import Person
from data.serializers.ocr import PassportImageSerializer
from data.views.ocr import extract_passport_info


def normalize_name(name):
    """Normalize name by removing special characters and converting to lowercase"""
    if not name:
        return ""
    return "".join(c.lower() for c in name if c.isalnum())

def calculate_person_match_score(person, mrz_data):
    """Calculate match score between Person object and MRZ data"""
    if not mrz_data:
        return 0
    
    score = 0
    max_score = 0
    
    # Helper function to compare fields using fuzzy matching
    def compare_fields(person_field, mrz_field, weight=1):
        if not person_field or not mrz_field:
            return 0, weight
        
        # Handle JSON fields that might contain lists
        if isinstance(person_field, list):
            person_value = person_field[0] if person_field else ""
        else:
            person_value = person_field
            
        return fuzz.ratio(str(person_value).lower(), str(mrz_field).lower()) * weight, weight

    # Compare names
    if person.firstName and person.lastName:
        name_score, weight = compare_fields(
            f"{person.firstName[0]} {person.lastName[0]}" if person.firstName and person.lastName else "",
            f"{mrz_data.get('names', '')} {mrz_data.get('surname', '')}",
            weight=3
        )
        score += name_score
        max_score += 100 * weight

    # Compare passport number
    if person.passportNumber:
        passport_score, weight = compare_fields(
            person.passportNumber[0] if person.passportNumber else "",
            mrz_data.get('number', ''),
            weight=4
        )
        score += passport_score
        max_score += 100 * weight

    # Compare birth date
    if person.birthDate:
        birth_score, weight = compare_fields(
            person.birthDate[0] if person.birthDate else "",
            mrz_data.get('date_of_birth', ''),
            weight=2
        )
        score += birth_score
        max_score += 100 * weight

    # Compare nationality
    if person.nationality:
        nationality_score, weight = compare_fields(
            person.nationality[0] if person.nationality else "",
            mrz_data.get('nationality', ''),
            weight=1
        )
        score += nationality_score
        max_score += 100 * weight

    return (score / max_score * 100) if max_score > 0 else 0

def find_matching_person(mrz_data):
    """Find the most matching Person based on MRZ data"""
    if not mrz_data:
        return None
        
    # Get all persons that might match based on basic criteria
    potential_matches = Person.objects.filter(
        Q(passportNumber__contains=mrz_data.get('number', '')) |
        (Q(firstName__isnull=False) & Q(lastName__isnull=False))
    )

    # Calculate match scores for each potential match
    matches_with_scores = [
        (person, calculate_person_match_score(person, mrz_data))
        for person in potential_matches
    ]
    
    # Sort by score in descending order
    matches_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return the best match if it has a score above threshold
    if matches_with_scores and matches_with_scores[0][1] >= 60:  # 60% threshold
        return matches_with_scores[0][0]
    
    return None

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class PassportOCRLookup(APIView):
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