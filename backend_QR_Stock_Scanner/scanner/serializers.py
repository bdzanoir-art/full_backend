from rest_framework import serializers
from .models import Material, StockTransaction

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class StockTransactionSerializer(serializers.ModelSerializer):
    material_title = serializers.ReadOnlyField(source='material.title')
    
    class Meta:
        model = StockTransaction
        fields = ['id', 'material', 'material_title', 'transaction_type', 'quantity', 'timestamp']
