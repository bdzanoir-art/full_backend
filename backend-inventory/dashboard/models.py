from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Material(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('In Use', 'In Use'),
        ('Maintenance', 'Maintenance'),
        ('Unavailable', 'Unavailable'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='materials')
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, default='General Lab')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Request(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    
    project_name = models.CharField(max_length=200)
    requester_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    item_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.project_name} - {self.requester_name}"

class MaintenanceAlert(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    issue = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.material.title}"

class MaterialOutput(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    destination = models.CharField(max_length=200)
    output_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.material.title} to {self.destination}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Lab Admin', 'Lab Admin'),
        ('Storekeeper', 'Storekeeper'),
        ('Student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
