from rest_framework import serializers
from .models import Material, Category, Request, MaintenanceAlert, UserProfile, Project, MaterialOutput
from django.contrib.auth.models import User

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
    category_name = serializers.CharField(source='category.name', read_only=True)
    qty = serializers.IntegerField(source='quantity', read_only=True)
    desc = serializers.CharField(source='description', read_only=True)
    
    class Meta:
        model = Material
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

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
