import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'treatment_center.settings'
django.setup()

def check_database_connection():
    from django.db import connections
    try:
        connections['default'].ensure_connection()
        print("✅ Database Connection: Successful")
        return True
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return False

def check_static_files():
    from django.conf import settings
    import os
    
    static_root = settings.STATIC_ROOT
    if os.path.exists(static_root):
        print(f"✅ Static Files Directory: {static_root} exists")
        return True
    else:
        print(f"❌ Static Files Directory Not Found: {static_root}")
        return False

def check_media_files():
    from django.conf import settings
    import os
    
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        print(f"✅ Media Files Directory: {media_root} exists")
        return True
    else:
        print(f"❌ Media Files Directory Not Found: {media_root}")
        return False

def main():
    print("=== Django Application Health Check ===")
    
    # Check Django settings
    from django.conf import settings
    print(f"Django Version: {django.get_version()}")
    print(f"Project Root: {settings.BASE_DIR}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")
    
    # Run checks
    checks = [
        check_database_connection,
        check_static_files,
        check_media_files
    ]
    
    failed_checks = [check.__name__ for check in checks if not check()]
    
    if failed_checks:
        print("\n❌ Some health checks failed:")
        for check in failed_checks:
            print(f"   - {check}")
        sys.exit(1)
    else:
        print("\n✅ All health checks passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()
