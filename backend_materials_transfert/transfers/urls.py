from django.urls import path
from .views import TransferListCreateView, TransferDetailView

urlpatterns = [
    path('transfers/', TransferListCreateView.as_view(), name='transfer-list'),
    path('transfers/<int:pk>/', TransferDetailView.as_view(), name='transfer-detail'),
]
