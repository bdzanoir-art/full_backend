"""
views.py — My Request app
All views: categories, materials, projects, material requests,
dashboard, login, validation.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from apps.core.models import Material, MaterialRequest, RequestItem, ValidationSlip, Student, Project, Category
from .serializers import (
    CategorySerializer, MaterialSerializer, StudentSerializer,
    ProjectSerializer, MaterialRequestSerializer, MaterialRequestCreateSerializer,
    RequestItemSerializer, ValidationSlipSerializer, DashboardSerializer,
)


class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'student_profile')


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.select_related('category').all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if cat := self.request.query_params.get('category', ''):
            queryset = queryset.filter(category_id=cat)
        if search := self.request.query_params.get('search', ''):
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(reference__icontains=search))
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            return Project.objects.filter(student=self.request.user.student_profile)
        return Project.objects.all()

    def perform_create(self, serializer):
        student = Student.objects.first()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
        serializer.save(student=student)


class MaterialRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        student = Student.objects.first()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
        queryset = MaterialRequest.objects.filter(student=student).prefetch_related('items')
        if sf := self.request.query_params.get('status', ''):
            queryset = queryset.filter(status=sf)
        if search := self.request.query_params.get('search', ''):
            queryset = queryset.filter(
                Q(request_number__icontains=search) | Q(project__name__icontains=search))
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return MaterialRequestCreateSerializer
        return MaterialRequestSerializer

    def perform_create(self, serializer):
        student = Student.objects.first()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
        serializer.save(student=student)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        mr = self.get_object()
        if mr.status == 'pending':
            mr.status = 'cancelled'
            mr.save()
            return Response({'status': 'cancelled', 'request_number': mr.request_number})
        return Response({'error': 'Only pending requests can be cancelled'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='slip')
    def validation_slip(self, request, pk=None):
        mr = self.get_object()
        slip, _ = ValidationSlip.objects.get_or_create(material_request=mr)
        return Response(ValidationSlipSerializer(slip, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    # Gracefully handle users without a student_profile (e.g., admins)
    if not hasattr(request.user, 'student_profile'):
        # Try to find a student record by user_id
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            # Return empty stats for non-student users instead of 403
            return Response({
                'total_requests': 0, 'pending_requests': 0,
                'approved_requests': 0, 'completed_requests': 0,
                'active_projects': 0, 'recent_requests': [],
            })
    else:
        student = request.user.student_profile

    requests_qs = MaterialRequest.objects.filter(student=student)
    return Response({
        'total_requests':     requests_qs.count(),
        'pending_requests':   requests_qs.filter(status='pending').count(),
        'approved_requests':  requests_qs.filter(status='approved').count(),
        'completed_requests': requests_qs.filter(status='completed').count(),
        'active_projects':    Project.objects.filter(student=student).count(),
        'recent_requests':    MaterialRequestSerializer(
            requests_qs.order_by('-created_at')[:5], many=True).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_validation(request, code):
    slip = get_object_or_404(ValidationSlip, validation_code=code)
    return Response(ValidationSlipSerializer(slip, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({'error': 'Email and password are required.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials.', 'details': 'User not found.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    user_auth = authenticate(username=user.username, password=password)
    if user_auth is None:
        return Response({'error': 'Invalid credentials.', 'details': 'Incorrect password.'},
                        status=status.HTTP_401_UNAUTHORIZED)
    if not user_auth.is_active:
        return Response({'error': 'Account disabled.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user_auth)
    student_profile = None
    if hasattr(user_auth, 'student_profile'):
        sp = user_auth.student_profile
        student_profile = {'student_id': sp.student_id, 'group': sp.group, 'department': sp.department}

    return Response({
        'message': 'Login successful',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user_auth.id, 'username': user_auth.username,
            'email': user_auth.email, 'first_name': user_auth.first_name,
            'last_name': user_auth.last_name,
            'full_name': user_auth.get_full_name() or user_auth.username,
        },
        'student_profile': student_profile,
    })
