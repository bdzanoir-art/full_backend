from django.urls import path
from .views import TransferListCreateView, TransferDetailView

urlpatterns = [
    path('',          TransferListCreateView.as_view(), name='transfer-list'),
    path('<int:pk>/', TransferDetailView.as_view(),     name='transfer-detail'),
]
