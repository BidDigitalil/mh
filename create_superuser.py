import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')
django.setup()

from treatment_app.models import User

# בדיקה אם המשתמש קיים
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='Admin123!',
        is_staff=True,
        is_superuser=True
    )
    print("משתמש אדמין נוצר בהצלחה")
