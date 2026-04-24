from django.db import models

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    from_lab = models.CharField(max_length=255)
    to_lab = models.CharField(max_length=255)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='Medium')
    reason = models.TextField()
    requested_by = models.CharField(max_length=255, default="Robotics Lab Admin")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def items_count(self):
        return self.items.count()

    @property
    def total_units(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return self.title

class TransferItem(models.Model):
    transfer = models.ForeignKey(Transfer, related_name='materials', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.name} for {self.transfer.title}"
