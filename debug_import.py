import sys
import os

# Add the project directory to Python path
project_dir = '/home/mh.bigdigital.co.il/public_html/treatment_center1'
sys.path.insert(0, project_dir)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')

# Attempt to set up Django and import modules
try:
    import django
    django.setup()
    
    print("Attempting to import crispy modules:")
    import crispy_forms
    print("Crispy Forms version:", crispy_forms.__version__)
    
    import crispy_bootstrap4
    print("Crispy Bootstrap4 path:", crispy_bootstrap4.__file__)
    
    # List all installed apps
    from django.apps import apps
    print("\nInstalled Apps:")
    for app_config in apps.get_app_configs():
        print(app_config.name)
except Exception as e:
    print(f"Error: {type(e).__name__} - {e}")
    import traceback
    traceback.print_exc()
