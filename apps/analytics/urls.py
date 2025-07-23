# URL patterns
from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.track_event, name='track_event'),
    path('trials/<int:trial_id>/metrics/', views.trial_analytics, name='trial_analytics'),
]