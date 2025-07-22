"""API views and endpoints."""
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.cache import cache_manager

from .analytics import SearchAnalytics
from .search_backends import ElasticsearchBackend


@api_view(["GET"])
@permission_classes([AllowAny])
@cache_manager.cache_page_response(timeout="short")
def search_trials(request):
    """Advanced search endpoint."""
    backend = ElasticsearchBackend()
    analytics = SearchAnalytics()

    # Get search parameters
    query = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 20))
    sort_by = request.GET.get("sort", "relevance")

    # Build filters
    filters = {}
    if request.GET.get("industry"):
        filters["industry"] = int(request.GET.get("industry"))
    if request.GET.get("location"):
        filters["location"] = request.GET.get("location")
    if request.GET.get("featured"):
        filters["is_featured"] = request.GET.get("featured") == "true"
    if request.GET.get("date_from") and request.GET.get("date_to"):
        filters["date_range"] = {"start": request.GET.get("date_from"), "end": request.GET.get("date_to")}

    # Perform search
    results = backend.search(query, filters, page, size, sort_by)

    # Track analytics only for authenticated users
    if request.user.is_authenticated:
        analytics.track_search(query, results["total"], filters, request.user.id)

    return Response(results)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_suggestions(request):
    """Autocomplete suggestions."""
    backend = ElasticsearchBackend()
    prefix = request.GET.get("q", "")

    if len(prefix) < 2:
        return Response({"suggestions": []})

    # Check cache first
    cache_key = f"search:suggest:{prefix}"
    suggestions = cache.get(cache_key)

    if not suggestions:
        suggestions = backend.suggest(prefix)
        cache.set(cache_key, suggestions, 300)  # 5 minutes

    return Response({"suggestions": suggestions})


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Changed from AllowAny
def track_search_click(request):
    """Track search result click."""
    analytics = SearchAnalytics()

    query = request.data.get("query")
    trial_id = request.data.get("trial_id")
    position = request.data.get("position", 0)

    if query and trial_id:
        analytics.track_click(query, trial_id, position, request.user.id)

    return Response({"status": "tracked"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Changed to require authentication
def search_analytics_dashboard(request):
    """Search analytics for admins."""
    if request.user.user_type != "admin":
        return Response({"error": "Unauthorized"}, status=403)

    analytics = SearchAnalytics()

    return Response(
        {
            "popular_searches": analytics.get_popular_searches(),
            "zero_results": analytics.get_zero_result_queries(),
            "click_through_rates": analytics.get_click_through_rate(),
        }
    )