from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'requests', views.MaterialRequestViewSet, basename='materialrequest')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login/', views.login, name='api_login'),
    path('api/dashboard/', views.dashboard, name='api_dashboard'),
    path('api/verify/<str:code>/', views.verify_validation, name='api_verify_validation'),
]
