from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

from data.amlmodels.customer_models import Customer
from data.amlmodels.flag_approval_models import FlagApproval
from data.amlmodels.verification_models import Verification
from data.amlmodels.search_history_model import SearchHistory
from data.serializers.search_history_serializer import SearchHistorySerializer

class DashboardStatisticsView(APIView):
    """
    API view to get dashboard statistics including total customers and flagged cases.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Get dashboard statistics.
        
        Returns:
            Response: JSON response with dashboard statistics
        """
        try:
            # Count total customers
            total_customers = Customer.objects.count()
            
            # Count flagged cases
            flagged_cases = FlagApproval.objects.count()
            
            # Get recent search history (limited to 5)
            recent_searches = []
            if request.user.is_authenticated:
                user_searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
                serializer = SearchHistorySerializer(user_searches, many=True)
                recent_searches = serializer.data
            
            # Get latest 10 flagged customers
            latest_flagged = FlagApproval.objects.select_related('user').order_by('-created_at')[:10]
            
            # Format the flagged customers data
            flagged_customers = []
            for flag in latest_flagged:
                # Try to get customer details if customer_id is available
                customer_data = {}
                if flag.customer_id:
                    try:
                        customer = Customer.objects.filter(id=flag.customer_id).first()
                        if customer:
                            customer_data = {
                                'id': customer.id,
                                'name': f"{customer.first_name} {customer.last_name}".strip(),
                                'email': customer.email,
                                'phone': customer.phone
                            }
                    except Exception:
                        # If customer not found, use basic data from flag
                        pass
                
                # Add flag data
                flagged_customers.append({
                    'flag_id': flag.id,
                    'customer_id': flag.customer_id,
                    'status': flag.status,
                    'reason_type': flag.get_reason_type_display() if hasattr(flag, 'get_reason_type_display') else flag.reason_type,
                    'details': flag.details,
                    'created_at': flag.created_at.isoformat(),
                    'flagged_by': flag.user.username if flag.user else None,
                    'customer': customer_data
                })
            
            # Get verification statistics by status
            verification_stats = Verification.objects.values('status').annotate(count=Count('status')).order_by('status')
            
            # Format verification statistics
            verification_by_status = {}
            for stat in verification_stats:
                status_key = stat['status'] if stat['status'] else 'unknown'
                verification_by_status[status_key] = stat['count']
            
            # Get total verifications
            total_verifications = sum(verification_by_status.values())
            
            # Get monthly compliance statistics for the last 6 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)  # Approximately 6 months
            
            # Get monthly flag approval statistics
            monthly_flag_stats = FlagApproval.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month', 'status').annotate(
                count=Count('id')
            ).order_by('month', 'status')
            
            # Format monthly compliance data
            compliance_data = {}
            for stat in monthly_flag_stats:
                month_str = stat['month'].strftime('%Y-%m')
                status_value = stat['status'] if stat['status'] else 'unknown'
                
                if month_str not in compliance_data:
                    compliance_data[month_str] = {}
                    
                compliance_data[month_str][status_value] = stat['count']
                
                # Calculate total for each month
                if 'total' not in compliance_data[month_str]:
                    compliance_data[month_str]['total'] = 0
                compliance_data[month_str]['total'] += stat['count']
            
            # Prepare response data
            data = {
                'message': 'Dashboard statistics retrieved successfully',
                'data': {
                    'total_customers': total_customers,
                    'flagged_cases': flagged_cases,
                    'total_transactions': 0,
                    'recent_activity': 0,
                    'recent_searches': recent_searches,
                    'latest_flagged_customers': flagged_customers,
                    'verification': {
                        'total': total_verifications,
                        'by_status': verification_by_status
                    },
                    'compliance': compliance_data
                }
            }
            
            return Response(data, status=http_status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    'message': 'Error retrieving dashboard statistics',
                    'error': str(e)
                },
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
