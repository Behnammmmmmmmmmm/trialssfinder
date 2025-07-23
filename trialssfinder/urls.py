import os
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.views.static import serve

from apps.core.views import health_check, metrics

def trigger_error(request):
    # Sentry debug endpoint
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Sentry debug endpoint
    path('sentry-debug/', trigger_error),
    
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
    # Serve static files manually in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Check if we're in development mode without React build
react_index_path = os.path.join(settings.BASE_DIR, 'trialsfinder', 'public', 'index.html')
if os.path.exists(react_index_path):
    # Use the public/index.html in development
    class DevIndexView(TemplateView):
        def get_template_names(self):
            return ['index.html']
    
    urlpatterns += [
        # Catch all other routes and serve index.html
        re_path(r'^(?!api|admin|static|media|health|metrics|sentry-debug).*$', 
                DevIndexView.as_view(), name='react_app'),
    ]
else:
    # Fallback template
    urlpatterns += [
        re_path(r'^.*$', TemplateView.as_view(template_name='fallback.html'), name='fallback'),
    ]