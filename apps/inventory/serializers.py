"""
serializers.py — Inventory app
"""

from rest_framework import serializers
from apps.core.models import Material, Category, Request, MaintenanceAlert, UserProfile, Project, MaterialOutput, Laboratory
from django.contrib.auth.models import User


class LaboratorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    materials_count = serializers.IntegerField(source='materials.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'materials_count']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    lab_name = serializers.SerializerMethodField()
    
    # Map frontend field names to backend model fields
    qty = serializers.IntegerField(source='quantity', required=False)
    desc = serializers.CharField(source='description', required=False, allow_blank=True)

    class Meta:
        model = Material
        fields = ['id', 'name', 'category', 'category_name', 'quantity', 'qty', 'quantity_available', 'description', 'desc', 'location', 'status', 'laboratory', 'lab_name', 'reference', 'qr_code', 'created_at']
        extra_kwargs = {
            'quantity': {'required': False},
            'description': {'required': False},
            'category': {'required': False, 'allow_null': True},
            'laboratory': {'required': False, 'allow_null': True},
        }

    def get_category_name(self, obj):
        return obj.category.name if obj.category else "Uncategorized"

    def get_lab_name(self, obj):
        return obj.laboratory.name if obj.laboratory else "General Lab"

    def create(self, validated_data):
        # Extract category and laboratory names from initial data
        category_name = self.initial_data.get('category_name') or self.initial_data.get('category')
        lab_name = self.initial_data.get('laboratory_name') or self.initial_data.get('lab')

        # Handle Category
        if category_name and not validated_data.get('category'):
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category
        
        # Handle Laboratory
        from apps.core.models import Laboratory
        if lab_name and not validated_data.get('laboratory'):
            import uuid
            lab, _ = Laboratory.objects.get_or_create(
                name=lab_name,
                defaults={'code': f"LAB-{uuid.uuid4().hex[:5].upper()}"}
            )
            validated_data['laboratory'] = lab
            
        # Ensure name is present
        if 'name' not in validated_data and 'title' in self.initial_data:
            validated_data['name'] = self.initial_data.get('title')
            
        # Default quantity_available
        if 'quantity_available' not in validated_data and 'quantity' in validated_data:
            validated_data['quantity_available'] = validated_data['quantity']

        return super().create(validated_data)


class RequestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='project_name', read_only=True)
    student = serializers.CharField(source='student_name', read_only=True)
    lab = serializers.CharField(default='Robotics Lab', read_only=True)
    date = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    qr = serializers.CharField(source='request_number', read_only=True)
    returnDate = serializers.DateField(source='end_date', read_only=True)
    issuedBy = serializers.CharField(default='Pending', read_only=True)
    actions = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = '__all__'

    def get_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else ''

    def get_materials(self, obj):
        # Join items into a single string for valid display
        items = obj.items.all()
        return ", ".join([f"{item.material.name} x{item.quantity}" for item in items]) or "No items"

    def get_actions(self, obj):
        # Define logic for what storekeeper can do based on status
        st = obj.status.lower()
        if st == 'pending':
            return ['Validate', 'Reject']
        if st == 'approved':
            return ['Mark Ready', 'View QR Code']
        if st == 'ready':
            return ['Confirm Pickup']
        if st == 'in use':
            return ['Confirm Return']
        return []


class MaintenanceAlertSerializer(serializers.ModelSerializer):
    material_title = serializers.CharField(source='material.title', read_only=True)

    class Meta:
        model = MaintenanceAlert
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'role']


class MaterialOutputSerializer(serializers.ModelSerializer):
    material_title = serializers.CharField(source='material.title', read_only=True)

    class Meta:
        model = MaterialOutput
        fields = '__all__'
