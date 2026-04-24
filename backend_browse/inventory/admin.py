from django.contrib import admin
from .models import Category, Material


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "key"]
    prepopulated_fields = {"key": ("name",)}
    search_fields = ["name"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "location", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]
