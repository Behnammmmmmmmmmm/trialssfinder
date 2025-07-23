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
    # Admin - removed duplicate namespace
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
    
    # Also serve from build directory if it exists
    build_dir = os.path.join(settings.BASE_DIR, 'trialsfinder', 'build')
    if os.path.exists(build_dir):
        urlpatterns += [
            re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(build_dir, 'static')}),
        ]

# Serve React app
# Check for React build
react_index_paths = [
    os.path.join(settings.BASE_DIR, 'trialsfinder', 'build', 'index.html'),
    os.path.join(settings.BASE_DIR, 'trialsfinder', 'dist', 'index.html'),
]

react_index_exists = any(os.path.exists(path) for path in react_index_paths)

if react_index_exists:
    # Serve index.html for all non-API routes
    urlpatterns += [
        re_path(r'^(?!api/|admin/|static/|media/|health/|metrics/|sentry-debug/).*$', 
                TemplateView.as_view(template_name='index.html'), name='react_app'),
    ]
else:
    # Development fallback
    fallback_template_path = os.path.join(settings.BASE_DIR, 'templates', 'fallback.html')
    if not os.path.exists(os.path.dirname(fallback_template_path)):
        os.makedirs(os.path.dirname(fallback_template_path))
    
    # Create fallback template if it doesn't exist
    if not os.path.exists(fallback_template_path):
        with open(fallback_template_path, 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrialsFinder - Build Required</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: #f8f9fa;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 600px;
        }
        h1 { color: #0056b3; }
        pre {
            background: #f1f3f5;
            padding: 1rem;
            border-radius: 4px;
            text-align: left;
            overflow-x: auto;
        }
        .api-link {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: #0056b3;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>React Build Required</h1>
        <p>The React application needs to be built first.</p>
        <pre>cd trialsfinder
npm install
npm run build</pre>
        <p>After building, refresh this page.</p>
        <a href="/api/" class="api-link">View API Endpoints</a>
    </div>
</body>
</html>''')
    
    urlpatterns += [
        re_path(r'^(?!api/|admin/|static/|media/|health/|metrics/|sentry-debug/).*$', 
                TemplateView.as_view(template_name='fallback.html'), name='fallback'),
    ]