from django.contrib import admin
from .models import Project, Category, Material, Request, MaintenanceAlert, MaterialOutput, UserProfile

admin.site.register(Project)
admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Request)
admin.site.register(MaintenanceAlert)
admin.site.register(MaterialOutput)
admin.site.register(UserProfile)
