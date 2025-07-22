"""API views and endpoints."""
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.throttling import EndpointThrottle

from .models import AnalyticsEvent
from .serializers import AnalyticsEventSerializer


class AnalyticsThrottle(EndpointThrottle):
    view_name = "analytics.track_event"


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Changed from AllowAny
@throttle_classes([AnalyticsThrottle])
def track_event(request):
    serializer = AnalyticsEventSerializer(data=request.data)
    if serializer.is_valid():
        # Always save with authenticated user
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trial_analytics(request, trial_id):
    if request.user.user_type != "company":
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    # Verify the trial belongs to the user's company
    from apps.trials.models import Trial

    try:
        trial = Trial.objects.get(id=trial_id, company=request.user.company)
    except Trial.DoesNotExist:
        return Response({"error": "Trial not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    queryset = AnalyticsEvent.objects.filter(trial_id=trial_id)

    if start_date:
        # Parse the date string and make it timezone-aware
        start_datetime = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        queryset = queryset.filter(timestamp__gte=start_datetime)
    if end_date:
        # Parse the date string, add one day, and make it timezone-aware
        end_datetime = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        queryset = queryset.filter(timestamp__lte=end_datetime)

    views = queryset.filter(event_type="trial_view").count()
    clicks = queryset.filter(event_type="trial_start").count()
    conversions = clicks / views * 100 if views > 0 else 0

    # Weekly data
    end = timezone.now()
    start = end - timedelta(days=7)
    weekly_data = []

    for i in range(7):
        day = start + timedelta(days=i)
        day_views = queryset.filter(event_type="trial_view", timestamp__date=day.date()).count()
        day_clicks = queryset.filter(event_type="trial_start", timestamp__date=day.date()).count()
        weekly_data.append({"date": day.strftime("%Y-%m-%d"), "views": day_views, "clicks": day_clicks})

    # Monthly data
    monthly_data = []
    for i in range(30):
        day = end - timedelta(days=30 - i)
        day_events = queryset.filter(timestamp__date=day.date()).count()
        monthly_data.append({"date": day.strftime("%Y-%m-%d"), "events": day_events})

    return Response(
        {"views": views,
            "clicks": clicks,
            "conversions": conversions,
            "weekly_data": weekly_data,
            "monthly_data": monthly_data,
        }
    )