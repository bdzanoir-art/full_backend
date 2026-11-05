import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# ═══════════════════════════════════════════════════════════════════
# 1. CORE DOMAIN: Users, Categories, Materials
# ═══════════════════════════════════════════════════════════════════

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Super Admin', 'Super Admin'), ('Admin', 'Admin'), ('Lab Admin', 'Lab Admin'),
        ('Storekeeper', 'Storekeeper'), ('Student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    group = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name or self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    key = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Material(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'), ('In Use', 'In Use'),
        ('Maintenance', 'Maintenance'), ('Unavailable', 'Unavailable'),
    ]
    name = models.CharField(max_length=200, verbose_name="Title/Name")
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="materials")
    
    quantity = models.PositiveIntegerField(default=0)
    quantity_available = models.PositiveIntegerField(default=0) # alias for my_request
    unit = models.CharField(max_length=50, default='pieces')
    
    location = models.CharField(max_length=200, blank=True, default='Shelf A1')
    laboratory = models.ForeignKey('Laboratory', on_delete=models.SET_NULL, null=True, blank=True, related_name="materials")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to="materials/", blank=True, null=True)
    
    reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    qr_code = models.CharField(max_length=200, unique=True, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name


class Laboratory(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Maintenance', 'Maintenance'), ('Inactive', 'Inactive')]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=200, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_labs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.name

# ═══════════════════════════════════════════════════════════════════
# 2. PROJECTS & REQUESTS
# ═══════════════════════════════════════════════════════════════════

class Project(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('completed', 'Completed'), ('paused', 'Paused')]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="projects", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeamMembers(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class MaterialRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('ready', 'Ready'), ('in use', 'In Use'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    request_number = models.CharField(max_length=50, unique=True, editable=False, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="material_requests", null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="material_requests", null=True, blank=True)
    
    # Standalone fields if FKs not used
    project_name = models.CharField(max_length=200, blank=True)
    requester_name = models.CharField(max_length=200, blank=True)
    
    purpose = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, null=True)
    student_response = models.TextField(blank=True, null=True)
    
    # Simple item assignment (esi_gm style)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    items_count = models.IntegerField(default=1) # maps to item_count too
    quantity = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def item_count(self):
        return self.items_count

class RequestItem(models.Model):
    material_request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name="items")
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    quantity_approved = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.material.name} x{self.quantity}"

class ValidationSlip(models.Model):
    material_request = models.OneToOneField(MaterialRequest, on_delete=models.CASCADE, related_name="validation_slip")
    validation_code = models.CharField(max_length=100, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.validation_code:
            self.validation_code = f"VAL-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

@receiver(post_save, sender=MaterialRequest)
def create_validation_slip(sender, instance, **kwargs):
    if instance.status.lower() == 'approved':
        ValidationSlip.objects.get_or_create(material_request=instance)

# ═══════════════════════════════════════════════════════════════════
# 3. TRANSACTIONS & OPERATIONS
# ═══════════════════════════════════════════════════════════════════

class MaterialOutput(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'), ('returned', 'Returned'),
        ('overdue', 'Overdue'), ('transferred', 'Transferred'),
        ('lost', 'Lost'), ('damaged', 'Damaged'),
    ]
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'), ('good', 'Good'),
        ('fair', 'Fair'), ('poor', 'Poor'), ('damaged', 'Damaged'),
    ]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='outputs')
    quantity = models.IntegerField(default=1)
    
    # ESI-GM fields
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='outputs', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='borrowed_items')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='material_outputs')
    transferred_to = models.ForeignKey(Laboratory, on_delete=models.CASCADE, null=True, blank=True, related_name='received_outputs')
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='excellent')
    notes = models.TextField(blank=True)
    issued_by = models.CharField(max_length=100, blank=True)
    returned_to = models.CharField(max_length=100, blank=True)
    qr_code = models.CharField(max_length=200, blank=True)
    
    # Inventory alias field
    destination = models.CharField(max_length=200, blank=True)

    issued_date = models.DateTimeField(auto_now_add=True) # Also output_date alias
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def output_date(self):
        return self.issued_date

class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = [
        ('preventive', 'Preventive'), ('corrective', 'Corrective'),
        ('predictive', 'Predictive'), ('emergency', 'Emergency'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('overdue', 'Overdue'),
    ]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    description = models.TextField(blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MaintenanceAlert(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='alerts')
    title = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True) # alias issue
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    quantity = models.PositiveIntegerField(default=1)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return not self.is_resolved
    @property
    def issue(self):
        return self.message

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [('input', 'Input'), ('output', 'Output')]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('in-transit', 'In Transit'),
        ('delivered', 'Delivered'), ('rejected', 'Rejected'),
    ]
    PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Urgent', 'Urgent')]

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
        return self.materials.count()
    @property
    def total_units(self):
        return sum(item.quantity for item in self.materials.all())

class TransferItem(models.Model):
    transfer = models.ForeignKey(Transfer, related_name='materials', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)

class SystemSetting(models.Model):
    # System Info
    platform_version = models.CharField(max_length=50, default='ESI-GM v1.0.0')
    last_backup_date = models.DateField(null=True, blank=True)
    
    # Notifications
    low_stock_alerts = models.BooleanField(default=True)
    maintenance_reminders = models.BooleanField(default=True)
    request_notifications = models.BooleanField(default=True)
    
    # UI Theme
    primary_color = models.CharField(max_length=20, default='#6366f1')
    accent_colors = models.JSONField(default=list) 
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "System Settings"

# Aliases for compatibility with legacy inventory endpoints
Request = MaterialRequest 