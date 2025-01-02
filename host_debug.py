import os
import sys
import socket
import django

# Set up Django environment
sys.path.append('/home/mh.bigdigital.co.il/public_html/treatment_center1')
os.environ['DJANGO_SETTINGS_MODULE'] = 'treatment_center.settings'
django.setup()

from django.conf import settings

def print_debug_info():
    print("=== System Information ===")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    
    print("\n=== Network Information ===")
    print(f"Hostname (socket.gethostname()): {socket.gethostname()}")
    print(f"Fully Qualified Domain Name: {socket.getfqdn()}")
    
    try:
        print(f"IP Addresses: {socket.gethostbyname_ex(socket.gethostname())[2]}")
    except Exception as e:
        print(f"Could not resolve IP addresses: {e}")
    
    print("\n=== Django Settings ===")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"DEBUG: {settings.DEBUG}")
    
    print("\n=== Environment Variables ===")
    for key, value in os.environ.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    print_debug_info()
