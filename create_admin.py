import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')
django.setup()

from treatment_app.models import User

# יצירת משתמש אדמין אם לא קיים
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
