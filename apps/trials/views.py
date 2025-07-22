"""API views and endpoints."""
import json
from django.core.cache import cache
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.cache import invalidate_pattern

from .models import FavoriteTrial, Industry, Trial, UserIndustry
from .serializers import (
    TrialSerializer,
    IndustrySerializer,
    FavoriteTrialSerializer,
    UserIndustrySerializer
)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def get_cache_key(prefix, params):
    """Generate cache key from prefix and params."""
    import hashlib
    params_str = json.dumps(params, sort_keys=True)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    return f"{prefix}:{params_hash}"


@api_view(["GET"])
@permission_classes([AllowAny])
def list_trials(request):
    # Build cache key
    cache_params = {
        'search': request.GET.get('search', ''),
        'industry': request.GET.get('industry', ''),
        'location': request.GET.get('location', ''),
        'featured': request.GET.get('featured', ''),
        'page': request.GET.get('page', '1'),
        'page_size': request.GET.get('page_size', '20'),
    }
    
    # Try cache first for anonymous users
    if not request.user.is_authenticated:
        cache_key = get_cache_key('trials_list', cache_params)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result)
    
    # Optimize query with select_related and only()
    queryset = Trial.objects.filter(status="approved").select_related(
        "industry", "company__user"
    ).only(
        "id", "title", "description", "location", "start_date", "end_date",
        "is_featured", "created_at", "updated_at",
        "industry__id", "industry__name",
        "company__id", "company__name", "company__user__id"
    )
    
    # Apply filters
    search = request.GET.get("search")
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    industry = request.GET.get("industry")
    if industry:
        queryset = queryset.filter(industry_id=industry)
    
    location = request.GET.get("location")
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    featured = request.GET.get("featured")
    if featured == "true":
        queryset = queryset.filter(is_featured=True)
    
    # Order by featured first, then by creation date
    queryset = queryset.order_by("-is_featured", "-created_at", "id")
    
    # Paginate
    page_size = request.GET.get("page_size")
    if page_size:
        try:
            paginator = StandardPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = TrialSerializer(page, many=True, context={"request": request})
                response_data = paginator.get_paginated_response(serializer.data).data
                
                # Cache for anonymous users
                if not request.user.is_authenticated:
                    cache.set(cache_key, response_data, 300)  # 5 minutes
                
                return Response(response_data)
        except Exception:
            pass
    
    # Return all results if no pagination
    serializer = TrialSerializer(queryset, many=True, context={"request": request})
    response_data = serializer.data
    
    # Cache for anonymous users
    if not request.user.is_authenticated:
        cache_key = get_cache_key('trials_list', cache_params)
        cache.set(cache_key, response_data, 300)  # 5 minutes
    
    return Response(response_data)


@api_view(["GET"])
@permission_classes([AllowAny])
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def list_industries(request):
    # Use database-level ordering and values for efficiency
    industries = Industry.objects.values("id", "name").order_by("name")
    return Response(list(industries))


@api_view(["GET"])
@permission_classes([AllowAny])
def trial_detail(request, pk):
    # Cache key for trial detail
    cache_key = f"trial_detail:{pk}"
    
    # Check cache first
    cached_trial = cache.get(cache_key)
    if cached_trial is not None:
        # Add user-specific data if authenticated
        if request.user.is_authenticated:
            cached_trial['is_favorited'] = FavoriteTrial.objects.filter(
                user=request.user, trial_id=pk
            ).exists()
        return Response(cached_trial)
    
    try:
        # Optimize query
        trial = Trial.objects.select_related(
            "industry", "company__user"
        ).only(
            "id", "title", "description", "location", "start_date", "end_date",
            "status", "is_featured", "created_at", "updated_at", "price",
            "industry__id", "industry__name",
            "company__id", "company__name", "company__user__id"
        ).get(pk=pk)
    except Trial.DoesNotExist:
        return Response({"error": "Trial not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Invalid trial ID"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TrialSerializer(trial, context={"request": request})
    response_data = serializer.data
    
    # Cache the result (without user-specific data)
    cache_data = response_data.copy()
    cache_data.pop('is_favorited', None)
    cache.set(cache_key, cache_data, 600)  # 10 minutes
    
    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trial(request):
    if request.user.user_type != "company":
        return Response({"error": "Only companies can create trials"}, status=403)
    
    if not hasattr(request.user, "company"):
        return Response(
            {"error": "Company profile not found. Please complete your company profile first."}, 
            status=400
        )
    
    serializer = TrialSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(company=request.user.company)
        
        # Clear relevant caches
        invalidate_pattern("trials_list:")
        
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def company_trials(request):
    if not hasattr(request.user, "company"):
        return Response({"error": "No company profile found"}, status=404)
    
    # Cache key specific to company
    cache_key = f"company_trials:{request.user.company.id}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return Response(cached_result)
    
    trials = Trial.objects.filter(
        company=request.user.company
    ).select_related("industry").order_by("-created_at")
    
    serializer = TrialSerializer(trials, many=True, context={"request": request})
    response_data = serializer.data
    
    # Cache for 5 minutes
    cache.set(cache_key, response_data, 300)
    
    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, pk):
    trial = get_object_or_404(Trial, pk=pk)
    favorite, created = FavoriteTrial.objects.get_or_create(
        user=request.user, trial=trial
    )
    
    if not created:
        favorite.delete()
        message = "Removed from favorites"
    else:
        message = "Added to favorites"
    
    # Clear user's favorites cache
    cache.delete(f"user_favorites:{request.user.id}")
    
    return Response({"message": message})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_favorites(request):
    # Cache user favorites
    cache_key = f"user_favorites:{request.user.id}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return Response(cached_result)
    
    favorites = FavoriteTrial.objects.filter(
        user=request.user
    ).select_related(
        "trial__industry", "trial__company__user"
    ).order_by("-created_at")
    
    serializer = FavoriteTrialSerializer(favorites, many=True, context={"request": request})
    response_data = serializer.data
    
    # Cache for 10 minutes
    cache.set(cache_key, response_data, 600)
    
    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_industries(request):
    industry_ids = request.data.get("industries", [])
    
    # Validate industry IDs exist
    valid_ids = list(Industry.objects.filter(id__in=industry_ids).values_list("id", flat=True))
    
    # Remove existing and add new
    UserIndustry.objects.filter(user=request.user).delete()
    
    # Bulk create new relationships
    if valid_ids:
        user_industries = [
            UserIndustry(user=request.user, industry_id=ind_id) 
            for ind_id in valid_ids
        ]
        UserIndustry.objects.bulk_create(user_industries)
    
    # Clear user industries cache
    cache.delete(f"user_industries:{request.user.id}")
    
    return Response({"message": "Industries updated"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_industries(request):
    # Cache user industries
    cache_key = f"user_industries:{request.user.id}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return Response(cached_result)
    
    user_industries = UserIndustry.objects.filter(
        user=request.user
    ).select_related("industry").order_by("industry__name")
    
    serializer = UserIndustrySerializer(user_industries, many=True)
    response_data = serializer.data
    
    # Cache for 30 minutes
    cache.set(cache_key, response_data, 1800)
    
    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_trial(request, pk):
    if request.user.user_type != "admin":
        return Response({"error": "Admin access required"}, status=403)
    
    trial = get_object_or_404(Trial, pk=pk)
    trial.status = "approved"
    trial.save()
    
    # Clear caches
    invalidate_pattern("trials_list:")
    cache.delete(f"trial_detail:{pk}")
    cache.delete(f"company_trials:{trial.company_id}")
    
    # Trigger background task for notifications
    from .tasks import process_trial_approval
    try:
        process_trial_approval.delay(trial.id)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not send notifications: {e}")
    
    return Response({"message": "Trial approved"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_featured(request, pk):
    if request.user.user_type != "admin":
        return Response({"error": "Admin access required"}, status=403)
    
    trial = get_object_or_404(Trial, pk=pk)
    trial.is_featured = not trial.is_featured
    trial.save()
    
    # Clear caches
    invalidate_pattern("trials_list:")
    cache.delete(f"trial_detail:{pk}")
    
    return Response({"message": "Featured status updated"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_trials(request):
    if request.user.user_type != "admin":
        return Response({"error": "Admin access required"}, status=403)
    
    trials = Trial.objects.all().select_related(
        "industry", "company__user"
    ).order_by("-created_at")
    
    serializer = TrialSerializer(trials, many=True, context={"request": request})
    return Response(serializer.data)