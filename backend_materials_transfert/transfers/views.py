from rest_framework import generics
from rest_framework.response import Response
from .models import Transfer
from .serializers import TransferSerializer

class TransferListCreateView(generics.ListCreateAPIView):
    queryset = Transfer.objects.all().order_by('-created_at')
    serializer_class = TransferSerializer

class TransferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
