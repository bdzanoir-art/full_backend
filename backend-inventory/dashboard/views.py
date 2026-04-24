from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Material, Category, Request, MaintenanceAlert, UserProfile, Project, MaterialOutput
from .serializers import (
    RequestSerializer, 
    MaintenanceAlertSerializer, 
    CategorySerializer, 
    MaterialSerializer, 
    ProjectSerializer,
    UserProfileSerializer,
    MaterialOutputSerializer
)
from django.db.models import Count, Sum
from django.db import models
from django.contrib.auth.models import User

class DashboardStatsView(APIView):
    def get(self, request):
        total_materials = Material.objects.aggregate(total=Sum('quantity'))['total'] or 0
        available_items = Material.objects.filter(status='Available').aggregate(total=Sum('quantity'))['total'] or 0
        pending_requests = Request.objects.filter(status='Pending').count()
        maintenance_alerts = MaintenanceAlert.objects.filter(is_active=True).count()
        
        # Materials by Category (for chart)
        categories_query = Category.objects.annotate(count=Count('materials'))
        category_labels = [c.name for c in categories_query]
        category_counts = [c.count for c in categories_query]
        
        # Materials by Status (for chart)
        status_data = list(Material.objects.values('status').annotate(count=Count('id')))
        
        # Recent Requests
        recent_requests = Request.objects.all().order_by('-created_at')[:5]
        recent_requests_serializer = RequestSerializer(recent_requests, many=True)
        
        # Maintenance Alerts
        active_alerts = MaintenanceAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
        alerts_serializer = MaintenanceAlertSerializer(active_alerts, many=True)
        
        # User Overview
        user_counts = UserProfile.objects.values('role').annotate(count=Count('id'))
        role_map = {item['role']: item['count'] for item in user_counts}
        
        return Response({
            'stats': [
                {'title': 'Total Materials', 'value': total_materials, 'note': '+12% this month', 'iconKey': 'browse', 'iconColor': '#6ea8ff'},
                {'title': 'Available Items', 'value': available_items, 'note': '', 'iconKey': 'projects', 'iconColor': '#20c997'},
                {'title': 'Pending Requests', 'value': pending_requests, 'note': '', 'iconKey': 'requests', 'iconColor': '#e8ab2f'},
                {'title': 'Maintenance Alerts', 'value': maintenance_alerts, 'note': '', 'iconKey': 'maintenance', 'iconColor': '#ff6b81'},
            ],
            'charts': {
                'by_category': {
                    'labels': category_labels,
                    'counts': category_counts
                },
                'by_status': status_data,
            },
            'recent_requests': recent_requests_serializer.data,
            'maintenance_alerts_list': alerts_serializer.data,
            'user_overview': {
                'lab_admins': role_map.get('Lab Admin', 0),
                'storekeepers': role_map.get('Storekeeper', 0),
                'students': role_map.get('Student', 0),
            }
        })

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                profile = UserProfile.objects.get(user=user)
                # Map backend roles to frontend roles
                role_map = {
                    'Student': 'student',
                    'Storekeeper': 'storekeeper',
                    'Lab Admin': 'admin',
                    'Admin': 'superadmin'
                }
                role = role_map.get(profile.role, 'student')
                
                return Response({
                    'token': 'mock-jwt-token-' + role, # Simplified token
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': role
                    }
                })
        except User.DoesNotExist:
            pass
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)
            
        return Response({'error': 'Invalid credentials'}, status=401)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MaterialListView(generics.ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class RequestListCreateView(generics.ListCreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class RequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class RequestCancelView(APIView):
    def post(self, request, pk):
        try:
            req = Request.objects.get(pk=pk)
            req.status = 'Cancelled'
            req.save()
            return Response({'status': 'cancelled'})
        except Request.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

class RequestSlipView(APIView):
    def get(self, request, pk):
        try:
            req = Request.objects.get(pk=pk)
            # Mock validation slip data
            return Response({
                'id': req.id,
                'project_name': req.project_name,
                'requester_name': req.requester_name,
                'status': req.status,
                'created_at': req.created_at,
                'slip_number': f"SLIP-{req.id:04d}",
                'qr_code': 'mock-qr-code-data',
                'validation_date': req.created_at # Assuming validated at creation for demo
            })
        except Request.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

class MaterialOutputListView(generics.ListCreateAPIView):
    queryset = MaterialOutput.objects.all().order_by('-output_date')
    serializer_class = MaterialOutputSerializer

class MaintenanceAlertListView(generics.ListCreateAPIView):
    queryset = MaintenanceAlert.objects.all().order_by('-created_at')
    serializer_class = MaintenanceAlertSerializer

class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
