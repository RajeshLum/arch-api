from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import ActivityLogs
from data.serializers.activity_logs import ActivityLogsSerializer

class ActivityLogsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List activity logs (admin can see all, others only their own)"""
        if request.user.is_staff:
            logs = ActivityLogs.objects.all().order_by('-updated_at')
        else:
            logs = ActivityLogs.objects.filter(user=request.user).order_by('-updated_at')
        
        serializer = ActivityLogsSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create an activity log"""
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ActivityLogsSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Delete a specific activity log by ID (admin: any, user: only their own)"""
        log_id = request.data.get('id')

        if not log_id:
            return Response({'error': 'Log ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff and log.user != request.user:
            return Response({'error': 'You do not have permission to delete this log.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            log = ActivityLogs.objects.get(pk=log_id)
        except ActivityLogs.DoesNotExist:
            return Response({'error': 'Activity log not found.'}, status=status.HTTP_404_NOT_FOUND)

        log.delete()
        
        return Response({'message': 'Activity log deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
