import re

def parse_user_agent(user_agent_string):
    """
    Parse the user agent string to extract browser, version, OS, and device information.
    This is a simple parser and doesn't require external dependencies.
    
    Args:
        user_agent_string (str): The user agent string from the request
        
    Returns:
        dict: Dictionary containing browser, version, os, and device information
    """
    result = {
        'browser': 'Unknown',
        'browser_version': '',
        'os': 'Unknown',
        'device': 'Desktop'  # Default to desktop
    }
    
    if not user_agent_string:
        return result
    
    # Check for mobile devices
    if any(mobile_keyword in user_agent_string.lower() for mobile_keyword in 
           ['mobile', 'android', 'iphone', 'ipad', 'ipod']):
        result['device'] = 'Mobile'
    
    # Check for tablets
    if any(tablet_keyword in user_agent_string.lower() for tablet_keyword in 
           ['ipad', 'tablet']):
        result['device'] = 'Tablet'
    
    # Extract browser and version
    # Chrome
    chrome_match = re.search(r'Chrome/(\d+\.\d+)', user_agent_string)
    if chrome_match:
        result['browser'] = 'Chrome'
        result['browser_version'] = chrome_match.group(1)
    
    # Safari (but not Chrome)
    elif 'Safari' in user_agent_string and 'Chrome' not in user_agent_string:
        safari_match = re.search(r'Version/(\d+\.\d+)', user_agent_string)
        result['browser'] = 'Safari'
        if safari_match:
            result['browser_version'] = safari_match.group(1)
    
    # Firefox
    elif 'Firefox' in user_agent_string:
        firefox_match = re.search(r'Firefox/(\d+\.\d+)', user_agent_string)
        result['browser'] = 'Firefox'
        if firefox_match:
            result['browser_version'] = firefox_match.group(1)
    
    # Edge
    elif 'Edg' in user_agent_string:
        edge_match = re.search(r'Edg(?:e)?/(\d+\.\d+)', user_agent_string)
        result['browser'] = 'Edge'
        if edge_match:
            result['browser_version'] = edge_match.group(1)
    
    # Internet Explorer
    elif 'MSIE' in user_agent_string or 'Trident/' in user_agent_string:
        result['browser'] = 'Internet Explorer'
        ie_match = re.search(r'MSIE (\d+\.\d+)', user_agent_string)
        if ie_match:
            result['browser_version'] = ie_match.group(1)
    
    # Extract OS information
    if 'Windows' in user_agent_string:
        result['os'] = 'Windows'
        win_match = re.search(r'Windows NT (\d+\.\d+)', user_agent_string)
        if win_match:
            win_version = win_match.group(1)
            win_versions = {
                '10.0': 'Windows 10/11',
                '6.3': 'Windows 8.1',
                '6.2': 'Windows 8',
                '6.1': 'Windows 7',
                '6.0': 'Windows Vista',
                '5.2': 'Windows XP x64',
                '5.1': 'Windows XP',
            }
            result['os'] = win_versions.get(win_version, f"Windows (NT {win_version})")
    
    elif 'Macintosh' in user_agent_string or 'Mac OS X' in user_agent_string:
        result['os'] = 'macOS'
        mac_match = re.search(r'Mac OS X (\d+[._]\d+)', user_agent_string)
        if mac_match:
            result['os'] = f"macOS {mac_match.group(1).replace('_', '.')}"
    
    elif 'Linux' in user_agent_string and 'Android' not in user_agent_string:
        result['os'] = 'Linux'
    
    elif 'Android' in user_agent_string:
        result['os'] = 'Android'
        android_match = re.search(r'Android (\d+\.\d+)', user_agent_string)
        if android_match:
            result['os'] = f"Android {android_match.group(1)}"
    
    elif 'iOS' in user_agent_string or 'iPhone OS' in user_agent_string:
        result['os'] = 'iOS'
        ios_match = re.search(r'(?:iPhone OS|iOS) (\d+[._]\d+)', user_agent_string)
        if ios_match:
            result['os'] = f"iOS {ios_match.group(1).replace('_', '.')}"
    
    return result
