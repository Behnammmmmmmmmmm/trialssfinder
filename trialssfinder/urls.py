import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from django.http import HttpResponse
from apps.core.views import health_check, metrics

def serve_react_app(request, path=''):
    """Serve the React app index.html directly"""
    try:
        react_index = os.path.join(settings.BASE_DIR, 'trialsfinder', 'dist', 'index.html')
        with open(react_index, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except:
        # Fallback to template if React build doesn't exist
        from django.template import loader
        template = loader.get_template('fallback.html')
        return HttpResponse(template.render({}, request))

def serve_locales(request, lang, filename):
    """Serve locale files"""
    locale_path = os.path.join(settings.BASE_DIR, 'trialsfinder', 'public', 'locales', lang, filename)
    try:
        with open(locale_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='application/json')
    except:
        return HttpResponse('{}', content_type='application/json')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health and monitoring endpoints
    path('health/', health_check, name='health_check'),
    path('metrics/', metrics, name='metrics'),
    
    # API endpoints with trailing slashes
    path('api/', include('apps.core.urls')),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/companies/', include('apps.companies.urls')),
    path('api/trials/', include('apps.trials.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/admin/', include('apps.admin_dashboard.urls')),
    path('api/compliance/', include('apps.compliance.urls')),
    path('api/payments/', include('apps.payments.urls')),
    
    # Locales endpoint
    path('locales/<str:lang>/<str:filename>', serve_locales, name='serve_locales'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Check for React build
react_build_dir = os.path.join(settings.BASE_DIR, 'trialsfinder', 'dist')
react_public_dir = os.path.join(settings.BASE_DIR, 'trialsfinder', 'public')

if os.path.exists(react_build_dir):
    # Serve React build files
    urlpatterns += [
        # Serve specific files from public directory first
        path('favicon.ico', serve, {'document_root': react_public_dir, 'path': 'favicon.ico'}),
        path('favicon.svg', serve, {'document_root': react_public_dir, 'path': 'favicon.svg'}),
        path('manifest.json', serve, {'document_root': react_public_dir, 'path': 'manifest.json'}),
        path('robots.txt', serve, {'document_root': react_public_dir, 'path': 'robots.txt'}),
        path('logo192.png', serve, {'document_root': react_public_dir, 'path': 'logo192.png'}),
        path('logo512.png', serve, {'document_root': react_public_dir, 'path': 'logo512.png'}),
        path('logo192.svg', serve, {'document_root': react_public_dir, 'path': 'logo192.svg'}),
        path('logo512.svg', serve, {'document_root': react_public_dir, 'path': 'logo512.svg'}),
        path('service-worker.js', serve, {'document_root': react_public_dir, 'path': 'serviceWorker.js'}),
        path('search-icon.svg', serve, {'document_root': react_public_dir, 'path': 'search-icon.svg'}),
        path('screenshots/homepage.png', serve, {'document_root': react_public_dir, 'path': 'screenshots/homepage.png'}),
        path('screenshots/search.png', serve, {'document_root': react_public_dir, 'path': 'screenshots/search.png'}),
        
        # Serve static files from React build
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(react_build_dir, 'static')}),
        
        # Catch all other routes and serve React app
        re_path(r'^(?!api|admin|static|media|health|metrics|favicon|manifest|robots|logo|service-worker).*$', serve_react_app, name='react_app'),
    ]
else:
    # Development fallback
    urlpatterns += [
        re_path(r'^$', TemplateView.as_view(template_name='fallback.html'), name='home'),
        re_path(r'^(?!api|admin|static|media|health|metrics).*$', TemplateView.as_view(template_name='fallback.html'), name='fallback'),
    ]