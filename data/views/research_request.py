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

from data.models import ResearchRequest
from data.serializers.research_request import ResearchRequestSerializer

# list, add
class ResearchRequestListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            queryset = ResearchRequest.objects.all().order_by('-id')
        else:
            queryset = ResearchRequest.objects.filter(user=request.user).order_by('-id')

        # Apply pagination manually
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = ResearchRequestSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        
        files = request.FILES.getlist('document')

        file_paths = []
        for file in files:
            filename = f'{uuid.uuid4()}_{file.name}'
            path = default_storage.save(f'uploads/document/research_requests/{filename}', ContentFile(file.read()))
            file_paths.append(path)

        data = {
            'user': request.user.id,
            'customer_id': request.data.get('customer_id', ''),
            'document': file_paths,
            'status': 'pending',
        }
            
        serializer = ResearchRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResearchRequestDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_request(self, pk, user):
        if user.is_staff:
            return get_object_or_404(ResearchRequest, pk=pk)
        
        return get_object_or_404(ResearchRequest, pk=pk, user=user)

    def get(self, request, pk):
        research_request = self.get_request(pk, request.user)
        serializer = ResearchRequestSerializer(research_request)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        research_request = self.get_request(pk, request.user)
        
        update_data = {
            'customer_id': request.data.get('customer_id', research_request.customer_id),
            'priority': request.data.get('priority', research_request.priority),
            'status': request.data.get('status', research_request.status),
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
                
                path = default_storage.save(f'uploads/document/research_requests/{filename}', ContentFile(file.read()))
                file_paths.append(path)

            # Append new files to existing document list
            if isinstance(research_request.document, list):
                update_data['document'] = research_request.document + file_paths
            else:
                update_data['document'] = file_paths  # fallback if somehow not a list
        else:
            update_data['document'] = research_request.document
        
        serializer = ResearchRequestSerializer(research_request, data=update_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        request = self.get_request(pk, request.user)
        request.delete()
        
        return Response({"detail": "Research Request deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
