import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import Material, Category, Request, MaintenanceAlert, UserProfile
from django.contrib.auth.models import User

def seed():
    # Clear existing
    Material.objects.all().delete()
    Category.objects.all().delete()
    Request.objects.all().delete()
    MaintenanceAlert.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # Categories
    cat_names = [
        'Microcontrollers', 'Sensors', 'Displays', 'Actuators', 
        'Power Supply', 'Communication', 'Passive Components', 
        'Prototyping', 'Connectors'
    ]
    cats = {name: Category.objects.create(name=name) for name in cat_names}

    # Materials
    # Total 1882, Available 47
    # Main bulk of materials
    Material.objects.create(
        title='Arduino Uno R3', 
        category=cats['Microcontrollers'], 
        quantity=1000, 
        status='In Use',
        description='Standard microcontroller board based on the ATmega328P.',
        location='Cabinet A-1'
    )
    Material.objects.create(
        title='Ultrasonic Sensor HC-SR04', 
        category=cats['Sensors'], 
        quantity=835, 
        status='In Use',
        description='Ultrasonic ranging module provides 2cm - 400cm non-contact measurement function.',
        location='Drawer B-2'
    )
    Material.objects.create(
        title='Raspberry Pi 4 Model B', 
        category=cats['Prototyping'], 
        quantity=47, 
        status='Available',
        description='High-performance 64-bit quad-core processor with dual-display support.',
        location='Shelf C-3'
    )

    # Users
    def create_user(username, email, role, is_staff=False):
        if not User.objects.filter(username=username).exists():
            u = User.objects.create_user(username=username, email=email, password='password123', is_staff=is_staff)
            UserProfile.objects.create(user=u, role=role)
            return u
        return User.objects.get(username=username)

    # Sync with frontend demo accounts
    create_user('admin_user', 'a.admin@esi-sba.dz', 'Lab Admin', is_staff=True)
    create_user('keeper_user', 's.keeper@esi-sba.dz', 'Storekeeper')
    create_user('student_user', 'm.student@esi-sba.dz', 'Student')
    
    # Extra roles for overview
    create_user('admin2', 'admin2@esi-sba.dz', 'Lab Admin', is_staff=True)
    create_user('admin3', 'admin3@esi-sba.dz', 'Lab Admin', is_staff=True)
    create_user('admin4', 'admin4@esi-sba.dz', 'Lab Admin', is_staff=True)

    # Requests
    Request.objects.create(
        project_name='Robotics Arm Control',
        requester_name='Sarah Student',
        status='Pending',
        item_count=2
    )
    Request.objects.create(
        project_name='IoT Weather Station',
        requester_name='Sarah Student',
        status='Approved',
        item_count=2
    )
    Request.objects.create(
        project_name='IoT Weather Station',
        requester_name='Sarah Student',
        status='Completed',
        item_count=1
    )

    # Maintenance Alert
    MaintenanceAlert.objects.create(
        material=Material.objects.first(),
        issue='Need calibration',
        is_active=True
    )

    print("Dashboard seeding complete!")

if __name__ == '__main__':
    seed()
