import os
import sys

# הוסף את נתיב הפרויקט לסביבת Python
sys.path.append('/home/mh.bigdigital.co.il/public_html/treatment_center1')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')

application = get_wsgi_application()
