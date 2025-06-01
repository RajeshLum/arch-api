from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count

from data.amlmodels.aml_services_models import AmlService
from data.amlmodels.verification_models import Verification

class ServiceStatisticsView(APIView):
    """
    API view to get statistics for AML services including verification counts by status.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Get service statistics with verification counts by status.
        
        Returns:
            Response: JSON response with service statistics
        """
        try:
            # Get all services
            services = AmlService.objects.all()
            
            service_stats = []
            
            # For each service, get verification statistics
            for service in services:
                # Get total verifications for this service
                total_verifications = Verification.objects.filter(service_id=service.id).count()
                
                # Get verifications by status for this service
                status_counts = Verification.objects.filter(
                    service_id=service.id
                ).values('status').annotate(
                    count=Count('status')
                ).order_by('status')
                
                # Format status counts
                status_data = {}
                for item in status_counts:
                    status_key = item['status'] if item['status'] else 'unknown'
                    status_data[status_key] = item['count']
                
                # Add service stats to the result
                service_stats.append({
                    'id': service.id,
                    'service_name': service.service_name,
                    'service_category': service.service_category,
                    'service_category_display': service.get_service_category_display(),
                    'total_verifications': total_verifications,
                    'verification_by_status': status_data
                })
            
            # Prepare response data
            data = {
                'message': 'Service statistics retrieved successfully',
                'data': service_stats
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    'message': 'Error retrieving service statistics',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
