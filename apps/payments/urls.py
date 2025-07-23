import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from apps.core.views import health_check, metrics

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health and monitoring endpoints
    path("health/", health_check, name="health_check"),
    path("metrics/", metrics, name="metrics"),
    # API endpoints
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/companies/", include(("apps.companies.urls", "apps.companies"), namespace="companies")),
    path("api/trials/", include("apps.trials.urls")),
    path("api/industries/", include("apps.trials.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/admin/", include("apps.admin_dashboard.urls")),
    path("api/compliance/", include(("apps.compliance.urls", "apps.compliance"), namespace="compliance")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Manually serve static files for the React app
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

# Serve React app - must be last
# Check for React build in both possible locations
react_build_exists = False
for build_dir in ['build', 'dist']:
    if (settings.BASE_DIR / 'trialsfinder' / build_dir / 'index.html').exists():
        react_build_exists = True
        break

if react_build_exists:
    # Serve index.html for all non-API routes
    urlpatterns += [
        re_path(
            r"^(?!api|admin|static|media|health|metrics).*$",
            TemplateView.as_view(template_name="index.html"),
            name="react_app",
        ),
    ]
else:
    # Fallback for when React build doesn't exist
    urlpatterns += [
        re_path(r"^.*$", TemplateView.as_view(template_name="fallback.html"), name="fallback"),
    ]