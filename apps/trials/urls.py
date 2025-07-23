# URL patterns
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_trials, name='trials_list'),
    path('<int:pk>/', views.trial_detail, name='trial_detail'),
    path('create/', views.create_trial, name='create_trial'),
    path('company/', views.company_trials, name='company_trials'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.user_favorites, name='user_favorites'),
    path('industries/', views.list_industries, name='industries_list'),
    path('industries/follow/', views.follow_industries, name='follow_industries'),
    path('industries/user/', views.user_industries, name='user_industries'),
    path('<int:pk>/approve/', views.approve_trial, name='approve_trial'),
    path('<int:pk>/toggle-featured/', views.toggle_featured, name='toggle_featured'),
    path('admin/', views.admin_trials, name='admin_trials'),
]