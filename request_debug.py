import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'treatment_center.settings'
django.setup()

def print_request_debug():
    from django.conf import settings
    import socket

    print("=== Detailed Request Debugging ===")
    print(f"Server Hostname: {socket.gethostname()}")
    print(f"Fully Qualified Domain Name: {socket.getfqdn()}")
    
    print("\n=== Django Settings ===")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"SECURE_PROXY_SSL_HEADER: {getattr(settings, 'SECURE_PROXY_SSL_HEADER', 'Not Set')}")
    print(f"USE_X_FORWARDED_HOST: {getattr(settings, 'USE_X_FORWARDED_HOST', 'Not Set')}")
    
    print("\n=== Middleware ===")
    print("Installed Middleware:")
    for middleware in settings.MIDDLEWARE:
        print(f"  - {middleware}")

    print("\n=== Network Interfaces ===")
    import netifaces
    for interface in netifaces.interfaces():
        try:
            ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            print(f"{interface}: {ip}")
        except (ValueError, KeyError):
            pass

if __name__ == '__main__':
    print_request_debug()
