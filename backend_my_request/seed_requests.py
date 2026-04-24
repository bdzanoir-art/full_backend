import os
import django
import uuid
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from my_request.models import Student, Project, MaterialRequest, RequestItem, Material, Category

def seed():
    # 1. Ensure a student exists
    user, _ = User.objects.get_or_create(username='sarah_student', defaults={'first_name': 'Sarah', 'last_name': 'Student', 'email': 's.student@esi-sba.dz'})
    if _ or not hasattr(user, 'student_profile'):
        user.set_password('password123')
        user.save()
        student, _ = Student.objects.get_or_create(user=user, defaults={'student_id': 'ESI-2026-001'})
    else:
        student = user.student_profile

    # Default category if needed
    category, _ = Category.objects.get_or_create(name='Uncategorized')

    def get_or_create_material(name):
        mat, created = Material.objects.get_or_create(
            name=name,
            defaults={
                'category': category,
                'reference': f"REF-{abs(hash(name)) % 10000}",
                'quantity_available': 50,
                'unit': 'unit'
            }
        )
        return mat

    # 2. Robotics Arm Control (Pending)
    p1, _ = Project.objects.get_or_create(name='Robotics Arm Control', student=student)
    r1, _ = MaterialRequest.objects.get_or_create(
        project=p1,
        student=student,
        purpose='To build a 3-DOF robotics arm.',
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        status='pending'
    )
    RequestItem.objects.get_or_create(material_request=r1, material=get_or_create_material('Soldering Station'), quantity=1)
    RequestItem.objects.get_or_create(material_request=r1, material=get_or_create_material('Power Supply DC 0-30V'), quantity=2)

    # 3. IoT Weather Station (Approved)
    p2, _ = Project.objects.get_or_create(name='IoT Weather Station', student=student)
    r2, _ = MaterialRequest.objects.get_or_create(
        project=p2,
        student=student,
        purpose='Long-range weather monitoring system.',
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=2),
        status='approved'
    )
    RequestItem.objects.get_or_create(material_request=r2, material=get_or_create_material('Arduino Uno R3'), quantity=3)
    RequestItem.objects.get_or_create(material_request=r2, material=get_or_create_material('Multimeter Fluke 87V'), quantity=2)

    # 4. IoT Weather Station (Completed)
    r3, _ = MaterialRequest.objects.get_or_create(
        project=p2,
        student=student,
        purpose='Software development phase.',
        start_date=date.today() - timedelta(days=15),
        end_date=date.today() - timedelta(days=5),
        status='completed'
    )
    RequestItem.objects.get_or_create(material_request=r3, material=get_or_create_material('Laptop Dell Precision'), quantity=1)

    print("SUCCESS: Mock projects and requests seeded into the database!")

if __name__ == '__main__':
    seed()
