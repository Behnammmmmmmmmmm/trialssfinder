"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_trials, name="trials-list"),
    path("<int:pk>/", views.trial_detail, name="trial-detail"),
    path("create/", views.create_trial, name="create-trial"),
    path("company/", views.company_trials, name="company-trials"),
    path("<int:pk>/favorite/", views.toggle_favorite, name="toggle-favorite"),
    path("favorites/", views.user_favorites, name="user-favorites"),
    path("industries/", views.list_industries, name="industries-list"),
    path("industries/follow/", views.follow_industries, name="follow-industries"),
    path("industries/user/", views.user_industries, name="user-industries"),
    path("<int:pk>/approve/", views.approve_trial, name="approve-trial"),
    path("<int:pk>/toggle-featured/", views.toggle_featured, name="toggle-featured"),
    path("admin/", views.admin_trials, name="admin-trials"),
]
