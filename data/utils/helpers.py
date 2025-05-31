from ..models import ActivityLogs

def log_activity(user=None, activity='OTHER', description='', ip_address=None, location='', status='SUCCESS'):
    ActivityLogs.objects.create(
        user=user,
        activity=activity,
        description=description,
        ip_address=ip_address,
        location=location,
        status=status
    )
