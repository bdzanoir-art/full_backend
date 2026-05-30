from django.urls import path
from .views import (
    DashboardStatsView, LoginView, CategoryListView,
    MaterialListView, MaterialDetailView, ProjectListCreateView, RequestListCreateView,
    RequestDetailView, RequestCancelView, RequestSlipView, RequestUpdateStatusView,
    MaterialOutputListView, MaintenanceAlertListView, UserProfileListView,
    LaboratoryListView,
)

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(),   name='inv-dashboard-stats'),
    path('login/',           LoginView.as_view(),             name='inv-login'),
    path('categories/',      CategoryListView.as_view(),      name='inv-category-list'),
    path('materials/',       MaterialListView.as_view(),      name='inv-material-list'),
    path('materials/<int:pk>/', MaterialDetailView.as_view(),   name='inv-material-detail'),
    path('projects/',        ProjectListCreateView.as_view(), name='inv-project-list'),
    path('requests/',        RequestListCreateView.as_view(), name='inv-request-list'),
    path('requests/<int:pk>/',        RequestDetailView.as_view(), name='inv-request-detail'),
    path('requests/<int:pk>/cancel/', RequestCancelView.as_view(), name='inv-request-cancel'),
    path('requests/<int:pk>/update-status/', RequestUpdateStatusView.as_view(), name='inv-request-update-status'),
    path('requests/<int:pk>/slip/',   RequestSlipView.as_view(),   name='inv-request-slip'),
    path('outputs/',  MaterialOutputListView.as_view(),  name='inv-output-list'),
    path('alerts/',   MaintenanceAlertListView.as_view(), name='inv-alert-list'),
    path('users/',    UserProfileListView.as_view(),     name='inv-user-list'),
    path('laboratories/', LaboratoryListView.as_view(), name='inv-lab-list'),
]
