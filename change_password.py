import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')
django.setup()

from treatment_app.models import User
from django.contrib.auth.hashers import make_password

# עדכון סיסמה למשתמש admin
user = User.objects.get(username='admin')
user.password = make_password('Admin123!')
user.save()

print("הסיסמה עודכנה בהצלחה")
