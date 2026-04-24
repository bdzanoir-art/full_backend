from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Material, StockTransaction
from .serializers import MaterialSerializer, StockTransactionSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = StockTransaction.objects.all().order_by('-timestamp')
    serializer_class = StockTransactionSerializer

    @action(detail=False, methods=['post'])
    def scan(self, request):
        qr_code = request.data.get('qr_code')
        transaction_type = request.data.get('type') # 'input' or 'output'
        quantity = int(request.data.get('quantity', 1))

        if not qr_code:
            return Response({"error": "QR code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find material by QR code
        material = Material.objects.filter(qr_code=qr_code).first()
        
        if not material:
            # If not found, try to find by title as fallback (sometimes QR is just the name)
            material = Material.objects.filter(title=qr_code).first()
            
        if not material:
            # If still not found, create a placeholder material for the new QR code
            material = Material.objects.create(
                title=f"New Item ({qr_code})",
                qr_code=qr_code,
                quantity=0
            )

        # Update quantity
        if transaction_type == 'input':
            material.quantity += quantity
        elif transaction_type == 'output':
            if material.quantity < quantity:
                return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)
            material.quantity -= quantity
        else:
            return Response({"error": "Invalid transaction type"}, status=status.HTTP_400_BAD_REQUEST)
        
        material.save()

        # Create transaction record
        transaction = StockTransaction.objects.create(
            material=material,
            transaction_type=transaction_type,
            quantity=quantity
        )

        return Response({
            "status": "success",
            "material": MaterialSerializer(material).data,
            "transaction": StockTransactionSerializer(transaction).data
        })
