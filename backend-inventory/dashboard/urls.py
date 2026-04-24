from django.urls import path
from .views import (
    DashboardStatsView, LoginView, CategoryListView, 
    MaterialListView, ProjectListCreateView, RequestListCreateView,
    RequestDetailView, RequestCancelView, RequestSlipView,
    MaterialOutputListView, MaintenanceAlertListView, UserProfileListView
)

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('login/', LoginView.as_view(), name='login'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('materials/', MaterialListView.as_view(), name='material-list'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('requests/', RequestListCreateView.as_view(), name='request-list'),
    path('requests/<int:pk>/', RequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:pk>/cancel/', RequestCancelView.as_view(), name='request-cancel'),
    path('requests/<int:pk>/slip/', RequestSlipView.as_view(), name='request-slip'),
    path('outputs/', MaterialOutputListView.as_view(), name='output-list'),
    path('alerts/', MaintenanceAlertListView.as_view(), name='alert-list'),
    path('users/', UserProfileListView.as_view(), name='user-list'),
]
