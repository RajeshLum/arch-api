import socket
import json
from urllib.request import urlopen

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_country_code_from_ip(ip):
    """
    Get the country code from an IP address using ipinfo.io.
    Returns a two-letter country code (ISO 3166-1 alpha-2).
    """
    try:
        # Default to Bangladesh if we're on localhost or internal network
        if ip in ['127.0.0.1', 'localhost', '::1'] or ip.startswith('192.168.') or ip.startswith('10.'):
            return 'bd'
        
        # Use ipinfo.io to get country information
        response = urlopen(f'https://ipinfo.io/{ip}/json')
        data = json.load(response)
        
        # Return the country code (e.g., 'us', 'bd', etc.)
        return data.get('country', 'bd').lower()
    except Exception:
        # Default to Bangladesh if there's any error
        return 'bd'

def get_user_country(request):
    """
    Get the user's country from the request.
    First checks for a country header, then falls back to IP-based geolocation.
    """
    # First check if the country is specified in a header
    country_code = request.headers.get('X-User-Country')
    
    # If not in header, try to get it from the IP address
    if not country_code:
        ip = get_client_ip(request)
        country_code = get_country_code_from_ip(ip)
    
    return country_code.lower() if country_code else 'bd'  # Default to Bangladesh
