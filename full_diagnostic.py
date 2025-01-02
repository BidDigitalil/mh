import os
import sys
import django
import socket
import traceback

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'treatment_center.settings'

def print_detailed_diagnostic():
    print("=== Comprehensive Django Diagnostic ===")
    
    try:
        django.setup()
        from django.conf import settings
        
        print("\n--- Django Configuration ---")
        print(f"Base Directory: {settings.BASE_DIR}")
        print(f"Secret Key Length: {len(settings.SECRET_KEY)}")
        print(f"Debug: {settings.DEBUG}")
        print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")
        
        print("\n--- Environment Information ---")
        print(f"Python Version: {sys.version}")
        print(f"Django Version: {django.__version__}")
        
        print("\n--- Server Information ---")
        print(f"Hostname: {socket.gethostname()}")
        print(f"FQDN: {socket.getfqdn()}")
        
        try:
            from django.db import connections
            print("\n--- Database Connections ---")
            for alias in connections:
                print(f"Connection Alias: {alias}")
                conn = connections[alias]
                print(f"  Engine: {conn.settings_dict['ENGINE']}")
                print(f"  Name: {conn.settings_dict['NAME']}")
        except Exception as db_error:
            print(f"Database Connection Check Failed: {db_error}")
        
        print("\n--- Installed Apps ---")
        for app in settings.INSTALLED_APPS:
            print(f"  - {app}")
        
        print("\n--- Middleware ---")
        for middleware in settings.MIDDLEWARE:
            print(f"  - {middleware}")
    
    except Exception as e:
        print("\n!!! CRITICAL DIAGNOSTIC ERROR !!!")
        print(traceback.format_exc())

if __name__ == '__main__':
    print_detailed_diagnostic()
