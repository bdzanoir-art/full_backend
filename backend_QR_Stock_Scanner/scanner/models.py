from django.db import models

class Material(models.Model):
    title = models.CharField(max_length=200)
    qr_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, default='General Lab')

    def __str__(self):
        return f"{self.title} ({self.qr_code})"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('input', 'Input'),
        ('output', 'Output'),
    ]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.material.title} at {self.timestamp}"
