"""views.py — Browse app"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from apps.core.models import Material, Category
from .serializers import MaterialSerializer, CategorySerializer


@api_view(["GET"])
def material_list(request):
    """GET /api/browse/materials/?search=&category="""
    queryset = Material.objects.select_related("category").all()
    if search := request.query_params.get("search", "").strip():
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search))
    if cat_key := request.query_params.get("category", "").strip():
        if cat_key != "all":
            queryset = queryset.filter(category__key=cat_key)
            
    if status_filter := request.query_params.get("status", "").strip():
        if status_filter.lower() != "all":
            queryset = queryset.filter(status__iexact=status_filter)
    return Response(MaterialSerializer(queryset, many=True, context={"request": request}).data)


@api_view(["GET"])
def material_detail(request, pk):
    """GET /api/browse/materials/<pk>/"""
    try:
        material = Material.objects.select_related("category").get(pk=pk)
    except Material.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(MaterialSerializer(material, context={"request": request}).data)


@api_view(["GET"])
def category_list(request):
    """GET /api/browse/categories/"""
    categories = Category.objects.all().order_by("name")
    return Response(CategorySerializer(categories, many=True).data)
