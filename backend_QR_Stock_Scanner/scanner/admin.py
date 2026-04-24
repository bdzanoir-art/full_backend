from django.contrib import admin
from .models import Material, StockTransaction

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'qr_code', 'quantity', 'location')
    search_fields = ('title', 'qr_code')

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('material', 'transaction_type', 'quantity', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
