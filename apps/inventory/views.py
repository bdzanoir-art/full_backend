"""
views.py — Inventory app
All views: dashboard stats, login, categories, materials,
projects, requests, material outputs, alerts, user profiles.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.db.models import Count, Sum
from django.contrib.auth.models import User

from apps.core.models import Material, Category, Request, MaintenanceAlert, UserProfile, Project, MaterialOutput, Laboratory
from .serializers import (
    RequestSerializer, MaintenanceAlertSerializer, CategorySerializer,
    MaterialSerializer, ProjectSerializer, UserProfileSerializer, MaterialOutputSerializer,
    LaboratorySerializer,
)


class LaboratoryListView(generics.ListAPIView):
    queryset = Laboratory.objects.all()
    serializer_class = LaboratorySerializer
    permission_classes = [AllowAny]


class DashboardStatsView(APIView):
    def get(self, request):
        total_materials = Material.objects.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Available = Total units - (In Use units + Maintenance units + Damaged/Lost)
        # Simplest way: Sum of quantity_available for materials that are NOT in a broken/lost status
        available_items = Material.objects.exclude(
            status__in=['Under Maintenance', 'Damaged', 'Lost']
        ).aggregate(total=Sum('quantity_available'))['total'] or 0

        categories_query = Category.objects.annotate(count=Count('materials'))
        status_data = list(Material.objects.values('status').annotate(count=Count('id')))
        recent_requests = Request.objects.all().order_by('-created_at')[:5]
        active_alerts = MaintenanceAlert.objects.filter(is_resolved=False).order_by('-created_at')[:5]
        user_counts = UserProfile.objects.values('role').annotate(count=Count('id'))
        role_map = {item['role']: item['count'] for item in user_counts}

        return Response({
            'total_materials':    total_materials,
            'available_items':    available_items,
            'pending_requests':   Request.objects.filter(status='pending').count(),
            'active_alerts':      MaintenanceAlert.objects.filter(is_resolved=False).count(),
            'stats': [
                {'title': 'Total Materials',    'value': total_materials,   'note': '+12% this month', 'iconKey': 'inventory',    'iconColor': '#6ea8ff'},
                {'title': 'Available Items',    'value': available_items,   'note': 'In Stock',        'iconKey': 'package',      'iconColor': '#20c997'},
                {'title': 'Pending Requests',   'value': Request.objects.filter(status='pending').count(), 'note': 'Awaiting Action', 'iconKey': 'requests',     'iconColor': '#e8ab2f'},
                {'title': 'Maintenance Alerts', 'value': MaintenanceAlert.objects.filter(is_resolved=False).count(), 'note': 'Attention needed', 'iconKey': 'maintenance',  'iconColor': '#ff6b81'},
            ],
            'charts': {
                'by_category': {
                    'labels': [c.name for c in categories_query],
                    'counts': [c.count for c in categories_query],
                },
                'by_status': status_data,
            },
            'recent_requests': RequestSerializer(recent_requests, many=True).data,
            'maintenance_alerts_list': MaintenanceAlertSerializer(active_alerts, many=True).data,
            'user_overview': {
                'lab_admins':   role_map.get('Lab Admin', 0),
                'storekeepers': role_map.get('Storekeeper', 0),
                'students':     role_map.get('Student', 0),
            },
        })


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                profile = UserProfile.objects.get(user=user)
                role_map = {
                    'Student': 'student', 'Storekeeper': 'storekeeper',
                    'Lab Admin': 'admin', 'Admin': 'superadmin',
                }
                role = role_map.get(profile.role, 'student')
                return Response({
                    'token': f'mock-jwt-token-{role}',
                    'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': role},
                })
        except User.DoesNotExist:
            pass
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)
        return Response({'error': 'Invalid credentials'}, status=401)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MaterialListView(generics.ListCreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        if category := self.request.query_params.get('category'):
            queryset = queryset.filter(category_id=category)
        if search := self.request.query_params.get('search'):
            queryset = queryset.filter(name__icontains=search)
        return queryset


class MaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [AllowAny]


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class RequestListCreateView(generics.ListCreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        if st := self.request.query_params.get('status'):
            queryset = queryset.filter(status=st)
        if search := self.request.query_params.get('request_number'):
            queryset = queryset.filter(request_number=search)
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
            return Response({
                'id': req.id, 'project_name': req.project_name,
                'requester_name': req.requester_name, 'status': req.status,
                'created_at': req.created_at,
                'slip_number': f"SLIP-{req.id:04d}",
                'qr_code': 'mock-qr-code-data',
                'validation_date': req.created_at,
            })
        except Request.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class RequestUpdateStatusView(APIView):
    def post(self, request, pk):
        try:
            req = Request.objects.get(pk=pk)
            action = request.data.get('action', '').lower()
            
            # Map action strings to statuses
            status_map = {
                'validate': 'approved',
                'approve': 'approved',
                'reject': 'rejected',
                'mark ready': 'ready',
                'confirm pickup': 'in use',
                'confirm return': 'completed',
            }
            
            if new_status := status_map.get(action):
                req.status = new_status
                req.save()

                # Sync Material status
                if new_status == 'in use':
                    for item in req.items.all():
                        item.material.status = 'In Use'
                        item.material.save()
                elif new_status == 'completed':
                    for item in req.items.all():
                        item.material.status = 'Available'
                        item.material.save()

                return Response({'status': req.status})
            return Response({'error': 'Invalid action'}, status=400)
        except Request.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class MaterialOutputListView(generics.ListCreateAPIView):
    queryset = MaterialOutput.objects.all().order_by('-issued_date')
    serializer_class = MaterialOutputSerializer


class MaintenanceAlertListView(generics.ListCreateAPIView):
    queryset = MaintenanceAlert.objects.all().order_by('-created_at')
    serializer_class = MaintenanceAlertSerializer


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
