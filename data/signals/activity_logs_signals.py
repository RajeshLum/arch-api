from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from data.amlmodels.activity_logs_model import ActivityLogs
from django.contrib.auth import get_user_model
from data.utils.geolocation import get_user_country, get_client_ip
from data.utils.user_agent_parser import parse_user_agent

User = get_user_model()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    country = get_user_country(request)
    city = ''  # Add city detection if available
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent_data = parse_user_agent(user_agent_string)

    ActivityLogs.objects.create(
        user=user,
        activity='LOGIN',
        description='User logged in',
        ip_address=ip_address,
        country=country,
        city=city,
        browser=user_agent_data.get('browser', ''),
        browser_version=user_agent_data.get('browser_version', ''),
        os=user_agent_data.get('os', ''),
        device=user_agent_data.get('device', ''),
        status='SUCCESS',
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    country = get_user_country(request)
    city = ''  # Add city detection if available
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent_data = parse_user_agent(user_agent_string)

    ActivityLogs.objects.create(
        user=user,
        activity='LOGOUT',
        description='User logged out',
        ip_address=ip_address,
        country=country,
        city=city,
        browser=user_agent_data.get('browser', ''),
        browser_version=user_agent_data.get('browser_version', ''),
        os=user_agent_data.get('os', ''),
        device=user_agent_data.get('device', ''),
        status='SUCCESS',
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
