from django.contrib import admin
from .models import (
    UserProfile, Student, Category, Material, Laboratory,
    Project, TeamMembers, MaterialRequest, RequestItem, ValidationSlip,
    MaterialOutput, MaintenanceRecord, MaintenanceAlert,
    StockTransaction, Transfer, TransferItem
)

# Unified Admin
admin.site.register(UserProfile)
admin.site.register(Student)
admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Laboratory)
admin.site.register(Project)
admin.site.register(TeamMembers)
admin.site.register(MaterialRequest)
admin.site.register(RequestItem)
admin.site.register(ValidationSlip)
admin.site.register(MaterialOutput)
admin.site.register(MaintenanceRecord)
admin.site.register(MaintenanceAlert)
admin.site.register(StockTransaction)
admin.site.register(Transfer)
admin.site.register(TransferItem)
