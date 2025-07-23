import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from apps.core.views import health_check, metrics

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health and monitoring endpoints
    path('health/', health_check, name='health_check'),
    path('metrics/', metrics, name='metrics'),
    
    # API endpoints
    path('api/', include('apps.core.urls')),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/companies/', include('apps.companies.urls')),
    path('api/trials/', include('apps.trials.urls')),
    path('api/industries/', include('apps.trials.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/admin/', include('apps.admin_dashboard.urls')),
    path('api/compliance/', include('apps.compliance.urls')),
    path('api/payments/', include('apps.payments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Check for React build
react_build_dir = os.path.join(settings.BASE_DIR, 'trialsfinder', 'dist')
react_index_html = os.path.join(react_build_dir, 'index.html')

if os.path.exists(react_build_dir) and os.path.exists(react_index_html):
    # Serve React build files
    urlpatterns += [
        # Serve static files from React build
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(react_build_dir, 'static')}),
        # Catch all other routes and serve React app
        re_path(r'^(?!api|admin|static|media|health|metrics).*$', TemplateView.as_view(template_name='index.html'), name='react_app'),
    ]
else:
    # Development fallback
    urlpatterns += [
        re_path(r'^$', TemplateView.as_view(template_name='fallback.html'), name='home'),
        re_path(r'^(?!api|admin|static|media|health|metrics).*$', TemplateView.as_view(template_name='fallback.html'), name='fallback'),
    ]