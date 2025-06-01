from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from data.amlmodels.aml_services_models import AmlService
from data.serializers.aml_services import AmlServiceSerializer

class AmlServiceListCreateView(APIView):
    """
    API view to list all AML services or create a new one.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        List all AML services for the authenticated user (admin gets all).
        """
        if request.user.is_staff:
            queryset = AmlService.objects.all().order_by('-created_at')
        else:
            queryset = AmlService.objects.filter(user=request.user).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        if paginated_queryset is None:
            return Response({"message": "Pagination failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = AmlServiceSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """
        Create a new AML service for the authenticated user.
        """
        data = request.data.copy()
        serializer = AmlServiceSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AmlServiceDetailView(APIView):
    """
    API view to retrieve, update or delete an AML service.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_aml_service(self, pk, user):
        """
        Helper method to get an AML service by primary key.
        Admin users can access any service, regular users only their own.
        """
        if user.is_staff:
            return get_object_or_404(AmlService, pk=pk)
        
        return get_object_or_404(AmlService, pk=pk, user=user)
    
    def get(self, request, pk):
        """
        Retrieve an AML service.
        """
        obj = self.get_aml_service(pk, request.user)
        serializer = AmlServiceSerializer(obj)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        """
        Update an AML service.
        """
        obj = self.get_aml_service(pk, request.user)
        
        # Create a copy of the request data to avoid modifying the original
        update_data = request.data.copy()
        
        # Prevent changing the user
        if 'user' in update_data:
            del update_data['user']
        
        serializer = AmlServiceSerializer(obj, data=update_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete an AML service.
        """
        obj = self.get_aml_service(pk, request.user)
        obj.delete()
        
        return Response({"detail": "AML service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
