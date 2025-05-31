from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from data.models import FlagApproval
from data.serializers.flag_approval import FlagApprovalSerializer

# list, add
class FlagApprovalListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            queryset = FlagApproval.objects.all().order_by('-id')
        else:
            queryset = FlagApproval.objects.filter(user=request.user).order_by('-id')

        # Apply pagination manually
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = FlagApprovalSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        data['status'] = request.data.get('status', 'pending')
        
        serializer = FlagApprovalSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlagApprovalDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_flag_approval(self, pk, user):
        if user.is_staff:
            return get_object_or_404(FlagApproval, pk=pk)
        
        return get_object_or_404(FlagApproval, pk=pk, user=user)

    def get(self, request, pk):
        obj = self.get_flag_approval(pk, request.user)
        serializer = FlagApprovalSerializer(obj)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        obj = self.get_flag_approval(pk, request.user)
        
        update_data = {
            'verification_id': request.data.get('verification_id', obj.verification_id),
            'customer_id': request.data.get('customer_id', obj.customer_id),
            'status': request.data.get('status', obj.status),
            'reason_type': request.data.get('reason_type', obj.reason_type),
            'details': request.data.get('details', obj.details),
        }
        
        serializer = FlagApprovalSerializer(obj, data=update_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_flag_approval(pk, request.user)
        obj.delete()
        
        return Response({"detail": "Flag Approval entry deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
