"""
serializers.py — ESI-GM app
All serializers for the esi_gm models.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from apps.core.models import (
    Student, Project, TeamMembers, Material, Laboratory,
    MaterialOutput, MaterialRequest, MaintenanceRecord, MaintenanceAlert, UserProfile
)


# ── Auth serializers ──────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    # Extra fields sent by frontend
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    account_type = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'full_name', 'account_type']

    def validate(self, data):
        email = data.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Email is required"})

        # Derive username from email if not provided
        if not data.get('username'):
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            data['username'] = username

        # Handle password2 (confirm password)
        password = data.get('password')
        password2 = data.get('password2')
        if not password2:
            data['password2'] = password
        elif password != password2:
            raise serializers.ValidationError({"password": "Passwords don't match"})

        # Handle full_name to first_name/last_name
        full_name = data.get('full_name', '')
        if full_name and not data.get('first_name'):
            parts = full_name.strip().split(' ', 1)
            data['first_name'] = parts[0]
            if len(parts) > 1:
                data['last_name'] = parts[1]
            else:
                data['last_name'] = ''

        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        # Pop fields not in User model
        validated_data.pop('password2', None)
        full_name = validated_data.pop('full_name', '')
        account_type = validated_data.pop('account_type', 'Student')

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create UserProfile (role)
        UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': account_type if account_type else 'Student'}
        )

        # Create Student profile
        name = f"{user.first_name} {user.last_name}".strip()
        if not name:
            name = user.username
        
        Student.objects.get_or_create(
            user=user,
            defaults={'name': name, 'email': user.email}
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")
        user = authenticate(username=user.username, password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']


class UserManagementSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    laboratory = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'laboratory']

    def get_role(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.role
        return "Student"

    def get_laboratory(self, obj):
        # Placeholder for laboratory if needed
        return "N/A"


# ── Domain serializers ────────────────────────────────────────────────────────

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email']


class TeamMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembers
        fields = ['id', 'name', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    team_members = TeamMembersSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'student', 'student_name', 'team_members', 'created_at']

    def create(self, validated_data):
        return Project.objects.create(**validated_data)


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'quantity', 'unit', 'location', 'category', 'description']


class LaboratorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = ['id', 'name', 'code', 'location']


class MaterialRequestSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = MaterialRequest
        fields = ['id', 'project', 'project_name', 'items_count', 'status', 'created_at', 'updated_at']


class MaterialOutputSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    transferred_to_name = serializers.CharField(source='transferred_to.name', read_only=True)

    class Meta:
        model = MaterialOutput
        fields = [
            'id', 'material', 'material_name', 'quantity',
            'laboratory', 'laboratory_name',
            'student', 'student_name', 'project', 'project_name',
            'transferred_to', 'transferred_to_name',
            'issued_date', 'expected_return_date', 'actual_return_date',
            'status', 'condition', 'notes', 'issued_by', 'returned_to',
            'qr_code', 'created_at', 'updated_at',
        ]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_category = serializers.CharField(source='material.category', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'


class MaintenanceAlertSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = MaintenanceAlert
        fields = '__all__'
