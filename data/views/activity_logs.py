from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import ActivityLogs
from data.serializers.activity_logs import ActivityLogsSerializer
from data.utils.geolocation import get_user_country, get_client_ip
from data.utils.user_agent_parser import parse_user_agent

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
        """Create an activity log using logic consistent with activity_logs_signals.py"""
        from django.utils import timezone

        ip_address = get_client_ip(request)
        country = get_user_country(request)
        city = ''  # Add city detection if available
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent_data = parse_user_agent(user_agent_string)

        # Use provided data or sensible defaults
        activity = request.data.get('activity', 'OTHER')
        description = request.data.get('description', 'Random activity log')
        status_value = request.data.get('status', 'SUCCESS')

        log = ActivityLogs.objects.create(
            user=request.user,
            activity=activity,
            description=description,
            ip_address=ip_address,
            country=country,
            city=city,
            browser=user_agent_data.get('browser', ''),
            browser_version=user_agent_data.get('browser_version', ''),
            os=user_agent_data.get('os', ''),
            device=user_agent_data.get('device', ''),
            status=status_value,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        serializer = ActivityLogsSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
