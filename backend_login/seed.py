import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User

users_data = [
    {"username": "admin", "email": "a.admin@esi-sba.dz", "password": "password123", "is_superuser": True, "is_staff": True},
    {"username": "storekeeper", "email": "s.keeper@esi-sba.dz", "password": "password123"},
    {"username": "student", "email": "m.student@esi-sba.dz", "password": "password123"}
]

for data in users_data:
    if not User.objects.filter(email=data['email']).exists():
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        if data.get("is_superuser"):
            user.is_superuser = True
            user.is_staff = True
            user.save()
        print(f"Created user: {data['email']}")
    else:
        print(f"User already exists: {data['email']}")
