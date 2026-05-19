from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'materials',  views.MaterialViewSet)
router.register(r'projects',   views.ProjectViewSet,        basename='myreq-project')
router.register(r'requests',   views.MaterialRequestViewSet, basename='myreq-request')

urlpatterns = [
    path('', include(router.urls)),
    path('login/',              views.login,              name='myreq-login'),
    path('dashboard/',          views.dashboard,          name='myreq-dashboard'),
    path('verify/<str:code>/',  views.verify_validation,  name='myreq-verify'),
]
