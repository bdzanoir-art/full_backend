from django.urls import path
from . import views

urlpatterns = [
    path("materials/", views.material_list, name="material-list"),
    path("materials/<int:pk>/", views.material_detail, name="material-detail"),
    path("categories/", views.category_list, name="category-list"),
]
