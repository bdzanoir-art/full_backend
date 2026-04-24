from rest_framework import serializers
from .models import Material, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "key"]


class MaterialSerializer(serializers.ModelSerializer):
    # Flat fields the frontend expects
    category = serializers.CharField(source="category.name", read_only=True)
    categoryKey = serializers.CharField(source="category.key", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ["id", "title", "description", "category", "categoryKey", "location", "status", "quantity", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
