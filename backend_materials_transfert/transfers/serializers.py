from rest_framework import serializers
from .models import Transfer, TransferItem

class TransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferItem
        fields = ['id', 'name', 'quantity']

class TransferSerializer(serializers.ModelSerializer):
    materials = TransferItemSerializer(many=True)
    itemsCount = serializers.IntegerField(source='items_count', read_only=True)
    totalUnits = serializers.IntegerField(source='total_units', read_only=True)
    date = serializers.SerializerMethodField()
    fromLab = serializers.CharField(source='from_lab')
    toLab = serializers.CharField(source='to_lab')
    requestedBy = serializers.CharField(source='requested_by', read_only=True)

    class Meta:
        model = Transfer
        fields = ['id', 'title', 'status', 'fromLab', 'toLab', 'priority', 'reason', 'materials', 'itemsCount', 'totalUnits', 'date', 'requestedBy']

    def get_date(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")

    def create(self, validated_data):
        materials_data = validated_data.pop('materials')
        # DRF mapping populates from_lab toLab via source translation
        transfer = Transfer.objects.create(
            title=validated_data.get('title', 'New Transfer'),
            from_lab=validated_data.get('from_lab'),
            to_lab=validated_data.get('to_lab'),
            priority=validated_data.get('priority'),
            reason=validated_data.get('reason')
        )
        transfer.title = f"Transfer #{transfer.id}"
        transfer.save()

        for material_data in materials_data:
            TransferItem.objects.create(transfer=transfer, **material_data)
        
        return transfer
