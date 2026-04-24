from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import (
    Material, MaterialRequest, RequestItem, ValidationSlip,
    Student, Project, Category
)
from .serializers import (
    CategorySerializer, MaterialSerializer, StudentSerializer,
    ProjectSerializer, MaterialRequestSerializer, MaterialRequestCreateSerializer,
    RequestItemSerializer, ValidationSlipSerializer, DashboardSerializer
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
        category = self.request.query_params.get('category', '')
        search = self.request.query_params.get('search', '')
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(reference__icontains=search)
            )
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Temporarily mock student attribution for unauthenticated requests
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
            return Project.objects.filter(student=student)
        return Project.objects.all()

    def perform_create(self, serializer):
        student = Student.objects.first()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
        serializer.save(student=student)


class MaterialRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Temporarily mock student for unauthenticated tests
        student = Student.objects.first()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
            
        queryset = MaterialRequest.objects.filter(student=student).prefetch_related('items')
        status_filter = self.request.query_params.get('status', '')
        search = self.request.query_params.get('search', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(
                Q(request_number__icontains=search) |
                Q(project__name__icontains=search)
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return MaterialRequestCreateSerializer
        return MaterialRequestSerializer

    def perform_create(self, serializer):
        student = Student.objects.first()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
        serializer.save(student=student)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        material_request = self.get_object()
        if material_request.status == 'pending':
            material_request.status = 'cancelled'
            material_request.save()
            return Response({'status': 'cancelled', 'request_number': material_request.request_number})
        return Response(
            {'error': 'Only pending requests can be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'], url_path='slip')
    def validation_slip(self, request, pk=None):
        material_request = self.get_object()
        slip, created = ValidationSlip.objects.get_or_create(
            material_request=material_request
        )
        serializer = ValidationSlipSerializer(slip, context={'request': request})
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def dashboard(request):
    student = request.user.student_profile
    data = {
        'total_requests': MaterialRequest.objects.filter(student=student).count(),
        'pending_requests': MaterialRequest.objects.filter(student=student, status='pending').count(),
        'approved_requests': MaterialRequest.objects.filter(student=student, status='approved').count(),
        'completed_requests': MaterialRequest.objects.filter(student=student, status='completed').count(),
        'active_projects': Project.objects.filter(student=student, status='active').count(),
        'recent_requests': MaterialRequestSerializer(
            MaterialRequest.objects.filter(student=student)[:5], many=True
        ).data,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_validation(request, code):
    slip = get_object_or_404(ValidationSlip, validation_code=code)
    serializer = ValidationSlipSerializer(slip, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials.', 'details': 'User not found with this email.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user_auth = authenticate(username=user.username, password=password)

    if user_auth is None:
        return Response(
            {'error': 'Invalid credentials.', 'details': 'Incorrect password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user_auth.is_active:
        return Response(
            {'error': 'Account disabled.', 'details': 'This account is inactive.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user_auth)

    user_data = {
        'id': user_auth.id,
        'username': user_auth.username,
        'email': user_auth.email,
        'first_name': user_auth.first_name,
        'last_name': user_auth.last_name,
        'full_name': user_auth.get_full_name() or user_auth.username,
    }

    student_profile = None
    if hasattr(user_auth, 'student_profile'):
        sp = user_auth.student_profile
        student_profile = {
            'student_id': sp.student_id,
            'group': sp.group,
            'department': sp.department,
        }

    return Response({
        'message': 'Login successful',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': user_data,
        'student_profile': student_profile,
    }, status=status.HTTP_200_OK)
