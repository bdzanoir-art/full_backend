"""
Unified URL configuration — all backends wired in one file.

  /admin/                → Django admin panel
  /api/esi-gm/           → esi_gm app  (projects, auth, maintenance, materials)
  /api/inventory/        → inventory app (dashboard stats, requests)
  /api/scanner/          → scanner app  (QR stock scanning)
  /api/browse/           → browse app   (material catalog)
  /api/login/            → login_app    (simple login endpoint)
  /api/transfers/        → transfers app (lab-to-lab transfers)
  /api/my-request/       → my_request app (student material requests)
  /api/token/            → JWT token obtain
  /api/token/refresh/    → JWT token refresh
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # JWT
    path('api/token/',         TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),

    # ── ESI-GM (main: projects, materials, auth, maintenance) ──────────────
    path('api/esi-gm/', include('apps.esi_gm.urls')),

    # ── Inventory / Admin Dashboard ─────────────────────────────────────────
    path('api/inventory/', include('apps.inventory.urls')),

    # ── QR Stock Scanner ────────────────────────────────────────────────────
    path('api/scanner/', include('apps.scanner.urls')),

    # ── Browse Material Catalog ─────────────────────────────────────────────
    path('api/browse/', include('apps.browse.urls')),

    # ── Simple Login ────────────────────────────────────────────────────────
    path('api/login/', include('apps.login_app.urls')),

    # ── Materials Transfer ──────────────────────────────────────────────────
    path('api/transfers/', include('apps.transfers.urls')),

    # ── Student Material Requests ───────────────────────────────────────────
    path('api/my-request/', include('apps.my_request.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
