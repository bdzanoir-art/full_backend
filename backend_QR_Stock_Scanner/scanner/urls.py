from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'materials', MaterialViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
