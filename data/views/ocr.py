import os
import re
from pprint import pprint

import cv2
import pytesseract
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
