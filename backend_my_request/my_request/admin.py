from django.contrib import admin
from .models import Category, Material, Student, Project, MaterialRequest, RequestItem, ValidationSlip


class RequestItemInline(admin.TabularInline):
    model = RequestItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['reference', 'name', 'category', 'quantity_available', 'unit']
    list_filter = ['category']
    search_fields = ['name', 'reference']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'group', 'department']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']
    list_filter = ['department', 'group']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name']


@admin.register(MaterialRequest)
class MaterialRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'project', 'student', 'status', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['request_number', 'project__name']
    inlines = [RequestItemInline]


@admin.register(ValidationSlip)
class ValidationSlipAdmin(admin.ModelAdmin):
    list_display = ['validation_code', 'material_request', 'validated_at']
    search_fields = ['validation_code']
