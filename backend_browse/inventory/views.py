from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Material, Category
from .serializers import MaterialSerializer, CategorySerializer


@api_view(["GET"])
def material_list(request):
    """
    GET /api/materials/
    Query params:
      - search   : filter by title or description (case-insensitive)
      - category : filter by category slug key
    """
    queryset = Material.objects.select_related("category").all()

    search = request.query_params.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    category_key = request.query_params.get("category", "").strip()
    if category_key and category_key != "all":
        queryset = queryset.filter(category__key=category_key)

    serializer = MaterialSerializer(queryset, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def material_detail(request, pk):
    """GET /api/materials/<pk>/"""
    try:
        material = Material.objects.select_related("category").get(pk=pk)
    except Material.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MaterialSerializer(material, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def category_list(request):
    """GET /api/categories/ — used to populate the filter dropdown dynamically."""
    categories = Category.objects.all().order_by("name")
    serializer = CategorySerializer(categories, many=True)
https://github.com/Walid-01/Login.git    return Response(serializer.data)
