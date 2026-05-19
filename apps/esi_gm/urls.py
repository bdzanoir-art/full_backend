from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/',     views.register,           name='esi_gm-register'),
    path('login/',        views.login,               name='esi_gm-login'),
    path('logout/',       views.logout,              name='esi_gm-logout'),
    path('profile/',      views.profile,             name='esi_gm-profile'),
    path('system-stats/', views.get_system_stats,    name='esi_gm-system-stats'),

    # Super Admin & User Management
    path('superadmin/stats/', views.super_admin_stats, name='esi_gm-super-admin-stats'),
    path('superadmin/users/', views.user_management_list, name='esi_gm-user-management-list'),
    path('superadmin/users/<int:user_id>/', views.user_management_detail, name='esi_gm-user-management-detail'),

    # Dashboard
    path('dashboard/',    views.StudentDashboard,    name='esi_gm-dashboard'),

    # Projects
    path('create-project/',                                          views.create_project,        name='esi_gm-create-project'),
    path('projects/',                                                views.get_all_projects,      name='esi_gm-all-projects'),
    path('projects/<int:project_id>/',                               views.get_project_details,   name='esi_gm-project-details'),
    path('projects/<int:project_id>/update/',                        views.update_project,        name='esi_gm-update-project'),
    path('projects/<int:project_id>/delete/',                        views.delete_project,        name='esi_gm-delete-project'),
    path('projects/<int:project_id>/add-member/',                    views.add_team_member,       name='esi_gm-add-member'),
    path('projects/<int:project_id>/delete-member/<int:member_id>/', views.delete_team_member,    name='esi_gm-delete-member'),

    # Students
    path('students/',         views.get_students,        name='esi_gm-students'),
    path('students/current/', views.get_current_student, name='esi_gm-current-student'),

    # Materials & Labs
    path('materials/',    views.get_materials,    name='esi_gm-materials'),
    path('laboratories/', views.laboratory_list,  name='esi_gm-laboratories'),

    # Material Outputs
    path('material-outputs/',                          views.material_output_list,    name='esi_gm-outputs'),
    path('material-outputs/<int:output_id>/',          views.material_output_detail,  name='esi_gm-output-detail'),
    path('material-outputs/<int:output_id>/return/',   views.return_material,         name='esi_gm-return'),
    path('material-outputs/stats/',                    views.material_output_stats,   name='esi_gm-output-stats'),

    # Maintenance
    path('maintenance/stats/',                              views.maintenance_stats,          name='esi_gm-maintenance-stats'),
    path('maintenance/records/',                            views.maintenance_records,        name='esi_gm-maintenance-records'),
    path('maintenance/records/<int:record_id>/',            views.maintenance_record_detail,  name='esi_gm-maintenance-detail'),
    path('maintenance/records/<int:record_id>/complete/',   views.complete_maintenance,       name='esi_gm-complete-maintenance'),
    path('maintenance/alerts/',                             views.maintenance_alerts,         name='esi_gm-maintenance-alerts'),
    path('maintenance/alerts/<int:alert_id>/resolve/',      views.resolve_alert,              name='esi_gm-resolve-alert'),
    path('maintenance/materials-needing/',                  views.materials_needing_maintenance, name='esi_gm-materials-needing'),
    path('maintenance/schedule/',                           views.schedule_maintenance,       name='esi_gm-schedule-maintenance'),
]
