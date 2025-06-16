from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from data.amlmodels.template_models import TemplateTitle

class TemplateVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        template_id = request.data.get('template_id')
        import uuid
        import time

        file = request.FILES.get('file')

        if not template_id or not file:
            return Response({'error': 'template_id and file are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        allowed_extensions = ['.csv', '.xls', '.xlsx']
        filename, ext = os.path.splitext(file.name)
        if ext.lower() not in allowed_extensions:
            return Response({'error': 'Only CSV or Excel files are allowed (.csv, .xls, .xlsx).'}, status=status.HTTP_400_BAD_REQUEST)

        template = get_object_or_404(TemplateTitle, pk=template_id)

        # Rename the file to a 16-character unique name
        import random
        import string
        unique_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + ext

        # Store the file in media/uploads/templates
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'templates')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        file_url = os.path.join(settings.MEDIA_URL, 'uploads', 'templates', unique_name)

        return Response({
            'template': template.title,
            'file_name': unique_name,
            'file_url': file_url,
            'message': 'File uploaded and template verified.'
        }, status=status.HTTP_200_OK)
