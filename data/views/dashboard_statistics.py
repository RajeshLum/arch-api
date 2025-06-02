from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

from data.amlmodels.customer_models import Customer
from data.amlmodels.flag_approval_models import FlagApproval
from data.amlmodels.verification_models import Verification
from data.amlmodels.aml_services_models import AmlService

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
            
            # Get total verifications
            total_verifications = Verification.objects.count()
            
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
            
            # Format verification statistics with counts and percentages in a single structure
            verification_by_status = {}
            
            for stat in verification_stats:
                status_key = stat['status'] if stat['status'] else 'unknown'
                count = stat['count']
                percentage = (count / total_verifications) * 100 if total_verifications > 0 else 0
                
                verification_by_status[status_key] = {
                    'count': count,
                    'percentage': round(percentage, 2)
                }
            
            # Get paginated verifications data
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)
            try:
                page = int(page)
                page_size = int(page_size)
            except (TypeError, ValueError):
                page = 1
                page_size = 10
                
            paginator = PageNumberPagination()
            paginator.page_size = page_size
            
            verifications = Verification.objects.all().order_by('-created_at')
            paginated_verifications = paginator.paginate_queryset(verifications, request)
            
            # Format paginated verifications data
            verifications_data = []
            for verification in paginated_verifications:
                # Get customer info as a string
                customer_info = ""
                if verification.customer_id:
                    try:
                        customer = Customer.objects.filter(id=verification.customer_id).first()
                        if customer:
                            customer_info = f"{customer.first_name} {customer.last_name} ({customer.email})".strip()
                    except Exception:
                        pass
                
                # Get service name if service_id is available
                service_name = ""
                if verification.service_id:
                    try:
                        service = AmlService.objects.filter(id=verification.service_id).first()
                        if service:
                            service_name = service.service_name
                    except Exception:
                        pass
                
                verifications_data.append({
                    'id': verification.id,
                    'customer_id': verification.customer_id,
                    'info': customer_info,
                    'id_type': verification.id_type,
                    'service_id': verification.service_id,
                    'service_name': service_name,
                    'status': verification.status,
                    'created_at': verification.created_at.isoformat(),
                    'updated_at': verification.updated_at.isoformat()
                })
            
            # Create pagination response
            verifications_pagination = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': verifications_data
            }
            
            # Get service statistics
            services = AmlService.objects.all()
            service_stats = []
            
            # For each service, get verification statistics
            for service in services:
                # Get total verifications for this service
                total_service_verifications = Verification.objects.filter(service_id=service.id).count()
                
                # Get verifications by status for this service
                status_counts = Verification.objects.filter(
                    service_id=service.id
                ).values('status').annotate(
                    count=Count('status')
                ).order_by('status')
                
                # Format status counts with percentages in a single structure
                status_data = {}
                
                for item in status_counts:
                    status_key = item['status'] if item['status'] else 'unknown'
                    count = item['count']
                    percentage = (count / total_service_verifications) * 100 if total_service_verifications > 0 else 0
                    
                    status_data[status_key] = {
                        'count': count,
                        'percentage': round(percentage, 2)
                    }
                
                # Add service stats to the result
                service_stats.append({
                    'id': service.id,
                    'service_name': service.service_name,
                    'service_category': service.service_category,
                    'service_category_display': service.get_service_category_display(),
                    'total_verifications': total_service_verifications,
                    'verification_by_status': status_data
                })
            
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
                    'total_verifications': total_verifications,
                    'total_customers': total_customers,
                    'flagged_cases': flagged_cases,
                    'recent_activity': 0,
                    'latest_flagged_customers': flagged_customers,
                    'verification': {
                        'total': total_verifications,
                        'by_status': verification_by_status,
                        'paginated_data': verifications_pagination
                    },
                    'services': service_stats,
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
