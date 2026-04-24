from django.db import models
from django.contrib.auth.models import User
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=200, verbose_name="Material Name")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="materials")
    description = models.TextField(blank=True)
    quantity_available = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default="unit")
    reference = models.CharField(max_length=50, unique=True, verbose_name="Reference")

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"

    def __str__(self):
        return f"{self.reference} - {self.name}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=50, unique=True, verbose_name="Student ID")
    group = models.CharField(max_length=50, blank=True, verbose_name="Group")
    department = models.CharField(max_length=100, blank=True, verbose_name="Department")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    name = models.CharField(max_length=200, verbose_name="Project Name")
    description = models.TextField(blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="projects")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name


class MaterialRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    request_number = models.CharField(max_length=50, unique=True, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="material_requests")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="material_requests")
    purpose = models.TextField(verbose_name="Purpose")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name="Notes")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, null=True)  # ➕ NEW
    student_response = models.TextField(blank=True, null=True)  # ➕ NEW
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    # ➕ UML Methods
    def approve(self, admin_id):
        self.status = 'approved'
        self.save()

    def reject(self, reason):
        self.status = 'rejected'
        self.notes = reason
        self.save()

    def complete(self):
        self.status = 'completed'
        self.save()

    def allocate_items(self, allocs):
        for item_id, qty in allocs.items():
            RequestItem.objects.filter(id=item_id).update(quantity_approved=qty)

    def update_status(self, status):
        self.status = status
        self.save()


class RequestItem(models.Model):
    material_request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name="items")
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Quantity Requested")
    quantity_approved = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantity Approved")

    class Meta:
        verbose_name = "Request Item"
        verbose_name_plural = "Request Items"

    def __str__(self):
        return f"{self.material.name} x{self.quantity}"


class ValidationSlip(models.Model):
    material_request = models.OneToOneField(MaterialRequest, on_delete=models.CASCADE, related_name="validation_slip")
    validation_code = models.CharField(max_length=100, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Validation Slip"
        verbose_name_plural = "Validation Slips"

    def save(self, *args, **kwargs):
        if not self.validation_code:
            self.validation_code = f"VAL-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Slip - {self.validation_code}"


# ➕ Signals
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=MaterialRequest)
def create_validation_slip(sender, instance, **kwargs):
    if instance.status == 'approved':
        ValidationSlip.objects.get_or_create(material_request=instance)
