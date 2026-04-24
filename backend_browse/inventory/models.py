from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)          # Display name e.g. "Microcontrollers"
    key = models.SlugField(unique=True)               # Filter key e.g. "microcontrollers"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Material(models.Model):
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("In Use", "In Use"),
        ("Maintenance", "Maintenance"),
        ("Unavailable", "Unavailable"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="materials")
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Available")
    quantity = models.PositiveIntegerField(default=10) # default stock level
    image = models.ImageField(upload_to="materials/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
