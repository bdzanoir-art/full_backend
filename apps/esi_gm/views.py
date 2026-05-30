"""
views.py — ESI-GM app
All views: auth (register/login/logout/profile), dashboard,
projects, materials, laboratories, material outputs, maintenance.
"""

import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import (
    Student, Project, TeamMembers, Material, Laboratory,
    MaterialOutput, MaterialRequest, MaintenanceRecord, MaintenanceAlert, UserProfile,
    Transfer, TransferItem, Category, SystemSetting
)
from .serializers import (
    StudentSerializer, ProjectSerializer, TeamMembersSerializer,
    MaterialSerializer, LaboratorySerializer, MaterialOutputSerializer,
    MaterialRequestSerializer, MaintenanceRecordSerializer, MaintenanceAlertSerializer,
    RegisterSerializer, LoginSerializer, UserManagementSerializer,
    CategorySerializer, SystemSettingSerializer,
)


# ═══════════════════════════════════════════════════════════════════
# AUTH VIEWS
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def get_system_stats(request):
    """System statistics for the landing page."""
    return Response({
        'total_projects': Project.objects.count(),
        'total_materials': Material.objects.count(),
        'total_requests': MaterialRequest.objects.count(),
        'active_users': User.objects.count(),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user and return JWT tokens."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        role = "Student"
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
            
        student = getattr(user, 'student_profile', None)
        user_id = student.id if student else user.id

        return Response({
            'user': {
                'id': user_id, 'username': user.username,
                'email': user.email, 'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role,
            },
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
            'message': 'registration successful',
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login and return JWT tokens + student info."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        student, _ = Student.objects.get_or_create(
            user=user,
            defaults={'name': f"{user.first_name} {user.last_name}", 'email': user.email},
        )
        refresh = RefreshToken.for_user(user)
        role = "Student"
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
            
        return Response({
            'user': {
                'id': student.id if hasattr(student, 'id') else user.id, 'username': user.username,
                'email': user.email, 'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role,
            },
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
            'message': 'login successful',
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    role = 'Student'
    try:
        role = user.userprofile.role
    except Exception:
        pass
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name() or user.username,
        'role': role,
    })


@api_view(['POST'])
def logout(request):
    """Blacklist the refresh token."""
    try:
        token = RefreshToken(request.data.get('refresh_token'))
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════════════
# SUPER ADMIN & USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny]) # Change as needed
def super_admin_stats(request):
    total_users = User.objects.count()
    total_laboratories = Laboratory.objects.count()
    total_materials = Material.objects.count()
    total_requests = MaterialRequest.objects.count()

    lab_admins = UserProfile.objects.filter(role='Lab Admin').count()
    warehouse_managers = UserProfile.objects.filter(role='Storekeeper').count()
    students = UserProfile.objects.filter(role='Student').count()
    
    labs = Laboratory.objects.all()
    laboratories_data = []
    for lab in labs:
        materials_count = Material.objects.filter(location=lab.name).count()
        admin_n = "N/A"
        if lab.admin:
            admin_n = f"{lab.admin.first_name} {lab.admin.last_name}".strip() or lab.admin.username
            
        laboratories_data.append({
            'id': lab.id,
            'name': lab.name,
            'location': lab.location,
            'materials_count': materials_count,
            'capacity': 50,
            'admin_name': admin_n
        })

    return Response({
        'total_users': total_users,
        'total_laboratories': total_laboratories,
        'total_materials': total_materials,
        'total_requests': total_requests,
        'lab_admins': lab_admins,
        'warehouse_managers': warehouse_managers,
        'students': students,
        'laboratories_overview': laboratories_data,
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def user_management_list(request):
    if request.method == 'GET':
        users = User.objects.all().order_by('-date_joined')
        return Response(UserManagementSerializer(users, many=True).data)

    if request.method == 'POST':
        data = request.data
        email = data.get('email')
        # Frontend sends fullName, not name
        full_name = data.get('fullName', data.get('name', ''))
        role = data.get('role', 'Student')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic split for first/last name
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        if User.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use email prefix as username if not provided
        username = email.split('@')[0]
        # Make sure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        import string
        import random
        # Generate a random password of 10 characters
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        random_password = ''.join(random.choice(chars) for _ in range(10))

        user = User.objects.create_user(
            username=username,
            email=email,
            password=random_password,
            first_name=first_name,
            last_name=last_name
        )
        
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': role}
        )

        # Send email to the user with their new credentials
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            subject = 'Your New Account on ESI-GM'
            message = f"Hello {first_name},\n\nAn account has been created for you on ESI-GM with the role of {role}.\n\nYour login details are:\nEmail: {email}\nPassword: {random_password}\n\nPlease change your password after logging in.\n\nBest,\nESI-GM Team"
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@esi-sba.dz'),
                [email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

        return Response(UserManagementSerializer(user).data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
def user_management_detail(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        data = request.data
        if 'role' in data:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': data['role']}
            )
        return Response(UserManagementSerializer(user).data)
        
    elif request.method == 'DELETE':
        user.delete()
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def StudentDashboard(request):
    try:
        student = Student.objects.get(user=request.user)
        projects = Project.objects.filter(student=student)
        all_requests = MaterialRequest.objects.filter(student=student)
    except Student.DoesNotExist:
        projects = Project.objects.none()
        all_requests = MaterialRequest.objects.none()

    recent_projects = projects.order_by('-created_at')[:5]
    recent_requests = all_requests.order_by('-created_at')[:5]

    return Response({
        'stats': {
            'active_projects': projects.count(),
            'total_requests': all_requests.count(),
            'browse_materials': Material.objects.count(),
            'approved_requests': all_requests.filter(status__iexact='approved').count(),
            'pending_requests': all_requests.filter(status__iexact='pending').count(),
        },
        'projects': ProjectSerializer(projects, many=True).data,
        'recent_projects': ProjectSerializer(recent_projects, many=True).data,
        'recent_requests': MaterialRequestSerializer(recent_requests, many=True).data,
    })


# ═══════════════════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    data = request.data
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
    try:
        project = Project.objects.create(
            student=student, 
            name=data.get('name', 'New Project'), 
            description=data.get('description', '')
        )
        for member in data.get('team_members', []):
            TeamMembers.objects.create(project=project, name=member['name'], email=member['email'])
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_projects(request):
    try:
        student = Student.objects.get(user=request.user)
        projects = Project.objects.filter(student=student).order_by('-created_at')
    except Student.DoesNotExist:
        projects = Project.objects.none()
    
    return Response(ProjectSerializer(projects, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_project_details(request, project_id):
    try:
        return Response(ProjectSerializer(Project.objects.get(id=project_id)).data)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        project.name = request.data.get('name', project.name)
        project.description = request.data.get('description', project.description)
        project.save()
        return Response(ProjectSerializer(project).data)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_project(request, project_id):
    try:
        Project.objects.get(id=project_id).delete()
        return Response({'message': 'Project deleted'})
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_team_member(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        member = TeamMembers.objects.create(
            project=project, name=request.data['name'], email=request.data['email']
        )
        return Response(TeamMembersSerializer(member).data, status=status.HTTP_201_CREATED)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return Response({'error': f'Missing field: {e}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_team_member(request, project_id, member_id):
    try:
        TeamMembers.objects.get(id=member_id, project_id=project_id).delete()
        return Response({'message': 'Team member deleted'})
    except TeamMembers.DoesNotExist:
        return Response({'error': 'Team member not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_students(request):
    return Response(StudentSerializer(Student.objects.all(), many=True).data)


@api_view(['GET'])
def get_current_student(request):
    student = Student.objects.first()
    if student:
        return Response(StudentSerializer(student).data)
    return Response({'error': 'No student found'}, status=status.HTTP_404_NOT_FOUND)


# ═══════════════════════════════════════════════════════════════════
# MATERIALS & LABORATORIES
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET'])
def get_materials(request):
    return Response(MaterialSerializer(Material.objects.all(), many=True).data)


@api_view(['GET', 'POST'])
def laboratory_list(request):
    if request.method == 'GET':
        return Response(LaboratorySerializer(Laboratory.objects.all(), many=True).data)
    serializer = LaboratorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def laboratory_detail(request, lab_id):
    try:
        lab = Laboratory.objects.get(id=lab_id)
    except Laboratory.DoesNotExist:
        return Response({'error': 'Laboratory not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(LaboratorySerializer(lab).data)

    if request.method in ['PUT', 'PATCH']:
        serializer = LaboratorySerializer(lab, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        lab.delete()
        return Response({'message': 'Laboratory deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════
# MATERIAL OUTPUTS
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
def material_output_list(request):
    if request.method == 'GET':
        lab_id = request.GET.get('laboratory')
        status = request.GET.get('status')
        search = request.GET.get('search')

        # 1. Fetch MaterialOutputs
        outputs = MaterialOutput.objects.all().order_by('-issued_date')
        if lab_id:
            outputs = outputs.filter(laboratory_id=lab_id)
        if status:
            outputs = outputs.filter(status=status)
        if search:
            outputs = outputs.filter(
                Q(material__name__icontains=search) |
                Q(student__name__icontains=search) |
                Q(project__name__icontains=search)
            )
        
        output_data = MaterialOutputSerializer(outputs, many=True).data

        # 2. Fetch Transfers and convert to "Output" format
        transfers = Transfer.objects.all().order_by('-created_at')
        # If filtering by lab, check from_lab
        if lab_id:
            try:
                lab_name = Laboratory.objects.get(id=lab_id).name
                transfers = transfers.filter(from_lab=lab_name)
            except Laboratory.DoesNotExist:
                pass
        
        # Filter transfers by status if applicable
        if status == 'transferred' or not status:
            # All valid transfers are technically "transferred" outputs
            transfer_outputs = []
            for t in transfers:
                if t.status == 'rejected': continue
                # Each material in the transfer is an output
                for item in t.materials.all():
                    # Simple search on transfer items
                    if search and search.lower() not in item.name.lower(): continue

                    transfer_outputs.append({
                        'id': f"T-{t.id}-{item.id}",
                        'material_name': item.name,
                        'quantity': item.quantity,
                        'laboratory_name': t.from_lab,
                        'transferred_to_name': t.to_lab,
                        'issued_date': t.created_at.strftime("%Y-%m-%d"),
                        'status': 'transferred',
                        'condition': 'excellent',
                        'notes': t.reason,
                        'recipient_name': t.to_lab # Display destination lab as recipient
                    })
            output_data.extend(transfer_outputs)
            
        # 3. Fetch "In Use" requests and convert to "Output" format
        in_use_requests = MaterialRequest.objects.filter(status='in use').order_by('-updated_at')
        
        # Filter requests by status if applicable
        if status == 'borrowed' or not status:
            req_outputs = []
            for r in in_use_requests:
                # Material might be null if using standalone fields
                mat_name = r.material.name if r.material else r.project_name
                # Simple search
                if search and search.lower() not in mat_name.lower(): continue

                req_outputs.append({
                    'id': f"R-{r.id}",
                    'material_name': mat_name,
                    'quantity': r.quantity,
                    'laboratory_name': "Main Lab", # Default if not specified in request
                    'student_name': r.requester_name or (r.student.name if r.student else "Unknown"),
                    'project_name': r.project_name,
                    'issued_date': r.updated_at.strftime("%Y-%m-%d"),
                    'status': 'borrowed',
                    'condition': 'good', # Default
                    'notes': r.purpose,
                    'recipient_name': r.requester_name or "Student"
                })
            output_data.extend(req_outputs)

        return Response(output_data)
    serializer = MaterialOutputSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def material_output_detail(request, output_id):
    try:
        output = MaterialOutput.objects.get(id=output_id)
    except MaterialOutput.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(MaterialOutputSerializer(output).data)
    if request.method == 'PUT':
        serializer = MaterialOutputSerializer(output, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    output.delete()
    return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def return_material(request, output_id):
    try:
        output = MaterialOutput.objects.get(id=output_id)
        output.status = 'returned'
        output.actual_return_date = timezone.now().date()
        output.returned_to = request.data.get('returned_to', '')
        output.save()
        output.material.quantity += output.quantity
        output.material.save()
        return Response(MaterialOutputSerializer(output).data)
    except MaterialOutput.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def material_output_stats(request):
    outputs = MaterialOutput.objects.all()
    transfers = Transfer.objects.exclude(status='rejected')
    active_requests = MaterialRequest.objects.filter(status='in use')
    
    # Calculate combined stats
    total_outputs = outputs.count() + transfers.count() + active_requests.count()
    borrowed = outputs.filter(status='borrowed').count() + active_requests.count()
    returned = outputs.filter(status='returned').count()
    overdue = outputs.filter(status='overdue').count()
    transferred_combined = outputs.filter(status='transferred').count() + transfers.count()
    
    return Response({
        'total_outputs': total_outputs,
        'borrowed': borrowed,
        'returned': returned,
        'overdue': overdue,
        'transferred': transferred_combined,
        'lost': outputs.filter(status='lost').count(),
        'damaged': outputs.filter(status='damaged').count(),
    })


# ═══════════════════════════════════════════════════════════════════
# MAINTENANCE
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET'])
def maintenance_stats(request):
    today = timezone.now().date()
    next_30 = today + timedelta(days=30)
    return Response({
        'needs_attention': MaterialOutput.objects.filter(
            condition__in=['poor', 'damaged']).values('material').distinct().count(),
        'upcoming_30_days': MaintenanceRecord.objects.filter(
            next_maintenance_date__lte=next_30, next_maintenance_date__gte=today,
            status='scheduled').count(),
        'overdue': MaintenanceRecord.objects.filter(
            next_maintenance_date__lt=today, status='scheduled').count(),
        'total': MaintenanceRecord.objects.count(),
        'by_type': {t: MaintenanceRecord.objects.filter(maintenance_type=t).count()
                    for t in ['preventive', 'corrective', 'predictive', 'emergency']},
        'by_status': {s: MaintenanceRecord.objects.filter(status=s).count()
                      for s in ['scheduled', 'in_progress', 'completed', 'overdue']},
    })


@api_view(['GET'])
def maintenance_records(request):
    records = MaintenanceRecord.objects.all().order_by('-next_maintenance_date')
    if mid := request.GET.get('material_id'):
        records = records.filter(material_id=mid)
    if mtype := request.GET.get('type'):
        records = records.filter(maintenance_type=mtype)
    if st := request.GET.get('status'):
        records = records.filter(status=st)
    return Response(MaintenanceRecordSerializer(records, many=True).data)


@api_view(['GET', 'POST'])
def maintenance_record_detail(request, record_id=None):
    if request.method == 'POST':
        s = MaintenanceRecordSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        record = MaintenanceRecord.objects.get(id=record_id)
    except MaintenanceRecord.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    if request.method == 'GET':
        return Response(MaintenanceRecordSerializer(record).data)
    s = MaintenanceRecordSerializer(record, data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(['POST'])
def complete_maintenance(request, record_id):
    try:
        record = MaintenanceRecord.objects.get(id=record_id)
        record.status = 'completed'
        record.actual_completion_date = timezone.now().date()
        record.save()
        return Response(MaintenanceRecordSerializer(record).data)
    except MaintenanceRecord.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET'])
def maintenance_alerts(request):
    alerts = MaintenanceAlert.objects.filter(is_resolved=False).order_by('-priority', '-created_at')
    return Response(MaintenanceAlertSerializer(alerts, many=True).data)


@api_view(['POST'])
def resolve_alert(request, alert_id):
    try:
        alert = MaintenanceAlert.objects.get(id=alert_id)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({'message': 'Alert resolved'})
    except MaintenanceAlert.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET'])
def materials_needing_maintenance(request):
    today = timezone.now().date()
    return Response({
        'damaged_materials': list(
            MaterialOutput.objects.filter(condition__in=['poor', 'damaged'])
            .select_related('material')
            .values('material__id', 'material__name', 'material__category', 'condition')
            .distinct()
        ),
        'upcoming_maintenance': MaintenanceRecordSerializer(
            MaintenanceRecord.objects.filter(
                next_maintenance_date__lte=today + timedelta(days=30), status='scheduled'
            ).select_related('material'),
            many=True,
        ).data,
    })


@api_view(['POST'])
def schedule_maintenance(request):
    s = MaintenanceRecordSerializer(data=request.data)
    if s.is_valid():
        record = s.save()
        if record.maintenance_type == 'emergency':
            MaintenanceAlert.objects.create(
                material=record.material,
                title=f"Emergency Maintenance Required: {record.material.name}",
                message=record.description or f"Emergency maintenance scheduled for {record.next_maintenance_date}",
                priority='critical',
            )
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


# ═══════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)
    
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def system_settings(request):
    settings, created = SystemSetting.objects.get_or_create(id=1)
    if request.method == 'GET':
        return Response(SystemSettingSerializer(settings).data)
    
    serializer = SystemSettingSerializer(settings, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def platform_info(request):
    import shutil
    import platform
    total, used, free = shutil.disk_usage("C:\\" if os.name == 'nt' else "/")
    used_gb = round(used / (2**30), 2)
    total_gb = round(total / (2**30), 2)
    
    return Response({
        'platform_version': 'ESI-GM v1.2.0',
        'db_status': 'Connected',
        'storage_used': f"{used_gb} GB",
        'storage_total': f"{total_gb} GB",
        'os': platform.system(),
        'python_version': platform.python_version()
    })
