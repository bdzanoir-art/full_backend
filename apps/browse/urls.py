from django.urls import path
from . import views

urlpatterns = [
    path("materials/",        views.material_list,   name="browse-materials"),
    path("materials/<int:pk>/", views.material_detail, name="browse-material-detail"),
    path("categories/",       views.category_list,   name="browse-categories"),
]
