"""API views and endpoints."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.analytics.models import AnalyticsEvent
from apps.companies.models import Company
from apps.core.cache import cache_manager
from apps.subscriptions.models import Subscription
from apps.trials.models import Trial

from .models import AdminAction, SystemConfig
from .serializers import (
    AdminActionSerializer,
    CompanyAdminSerializer,
    DashboardStatsSerializer,
    SystemConfigSerializer,
    SystemHealthSerializer,
    TrialAdminSerializer,
    UserAdminSerializer,
)
from .tasks import bulk_process_trials, generate_admin_report

User = get_user_model()


class AdminPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


def log_admin_action(admin, action_type, target_model=None, target_id=None, details=None):
    """Log an admin action for audit trail."""
    AdminAction.objects.create(
        admin=admin,
        action_type=action_type,
        target_model=target_model or "",
        target_id=target_id,
        details=details or {},
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    # Try cache first
    cache_key = "admin:dashboard_stats"
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return Response(cached_stats)

    # Calculate stats
    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    stats = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(last_login__gte=last_30_days).count(),
        "new_users_30d": User.objects.filter(date_joined__gte=last_30_days).count(),
        "total_companies": Company.objects.count(),
        "total_trials": Trial.objects.count(),
        "pending_trials": Trial.objects.filter(status="under_review").count(),
        "approved_trials": Trial.objects.filter(status="approved").count(),
        "featured_trials": Trial.objects.filter(is_featured=True).count(),
        "total_revenue": Subscription.objects.filter(status="active").aggregate(Sum("amount"))["amount__sum"] or 0,
        "revenue_30d": Subscription.objects.filter(created_at__gte=last_30_days).aggregate(Sum("amount"))["amount__sum"]
        or 0,
        "total_events": AnalyticsEvent.objects.count(),
        "events_today": AnalyticsEvent.objects.filter(timestamp__date=now.date()).count(),
    }

    # Cache for 5 minutes
    cache.set(cache_key, stats, 300)
    return Response(stats)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def growth_metrics(request):
    days = int(request.GET.get("days", 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    metrics = []
    current_date = start_date

    while current_date <= end_date:
        metrics.append(
            {
                "date": current_date.isoformat(),
                "new_users": User.objects.filter(date_joined__date=current_date).count(),
                "new_trials": Trial.objects.filter(created_at__date=current_date).count(),
                "revenue": float(
                    Subscription.objects.filter(created_at__date=current_date).aggregate(Sum("amount"))["amount__sum"]
                    or 0
                ),
                "events": AnalyticsEvent.objects.filter(timestamp__date=current_date).count(),
            }
        )
        current_date += timedelta(days=1)

    return Response(metrics)


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def user_management(request):
    if request.method == "GET":
        queryset = User.objects.all()

        # Filters
        user_type = request.GET.get("user_type")
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        tier = request.GET.get("tier")
        if tier:
            queryset = queryset.filter(tier=tier)

        is_active = request.GET.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == "true")

        search = request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(username__icontains=search) | Q(email__icontains=search))

        # Sorting
        sort_by = request.GET.get("sort", "-date_joined")
        queryset = queryset.order_by(sort_by)

        paginator = AdminPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserAdminSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # Bulk actions
    action = request.data.get("action")
    user_ids = request.data.get("user_ids", [])

    if action == "ban":
        User.objects.filter(id__in=user_ids).update(is_active=False)
        log_admin_action(request.user, "bulk_action", "User", details={"action": "ban", "user_ids": user_ids})
    elif action == "unban":
        User.objects.filter(id__in=user_ids).update(is_active=True)
        log_admin_action(request.user, "bulk_action", "User", details={"action": "unban", "user_ids": user_ids})
    elif action == "change_tier":
        new_tier = request.data.get("new_tier")
        User.objects.filter(id__in=user_ids).update(tier=new_tier)
        log_admin_action(
            request.user,
            "bulk_action",
            "User",
            details={"action": "change_tier", "user_ids": user_ids, "new_tier": new_tier},
        )

    return Response({"message": f"{action} completed for {len(user_ids)} users"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def user_action(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    action = request.data.get("action")

    if action == "toggle_active":
        user.is_active = not user.is_active
        user.save()
        log_admin_action(request.user, "user_unbanned" if user.is_active else "user_banned", "User", user_id)
    elif action == "change_tier":
        new_tier = request.data.get("tier")
        user.tier = new_tier
        user.save()
        log_admin_action(
            request.user,
            "system_config",
            "User",
            user_id,
            {"field": "tier", "old_value": user.tier, "new_value": new_tier},
        )
    elif action == "reset_password":
        # Trigger password reset
        from django.utils.crypto import get_random_string

        user.reset_token = get_random_string(64)
        user.save()
        # Send email notification
        from apps.notifications.tasks import send_email_notification

        send_email_notification.delay(
            user.id, "Password Reset by Admin", "An administrator has initiated a password reset for your account."
        )

    return Response(UserAdminSerializer(user).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def trial_management(request):
    queryset = Trial.objects.select_related("company", "industry")

    # Filters
    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(status=status)

    is_featured = request.GET.get("is_featured")
    if is_featured is not None:
        queryset = queryset.filter(is_featured=is_featured == "true")

    industry = request.GET.get("industry")
    if industry:
        queryset = queryset.filter(industry_id=industry)

    search = request.GET.get("search")
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search) | Q(company__name__icontains=search)
        )

    # Sorting
    sort_by = request.GET.get("sort", "-created_at")
    queryset = queryset.order_by(sort_by)

    paginator = AdminPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = TrialAdminSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def trial_action(request, trial_id):
    try:
        trial = Trial.objects.get(id=trial_id)
    except Trial.DoesNotExist:
        return Response({"error": "Trial not found"}, status=404)

    action = request.data.get("action")

    if action == "approve":
        trial.status = "approved"
        trial.save()
        log_admin_action(request.user, "trial_approved", "Trial", trial_id)
        # Trigger notifications
        from apps.trials.tasks import process_trial_approval

        process_trial_approval.delay(trial_id)
    elif action == "reject":
        trial.status = "rejected"
        trial.save()
        log_admin_action(request.user, "trial_rejected", "Trial", trial_id)
    elif action == "toggle_featured":
        trial.is_featured = not trial.is_featured
        trial.save()
        log_admin_action(request.user, "trial_featured", "Trial", trial_id)
        cache_manager.invalidate_trial_cache(trial_id)

    return Response(TrialAdminSerializer(trial).data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def bulk_trial_action(request):
    action = request.data.get("action")
    trial_ids = request.data.get("trial_ids", [])

    if action == "approve":
        Trial.objects.filter(id__in=trial_ids, status="under_review").update(status="approved")
        bulk_process_trials.delay(trial_ids, "approve")
    elif action == "reject":
        Trial.objects.filter(id__in=trial_ids).update(status="rejected")
    elif action == "feature":
        Trial.objects.filter(id__in=trial_ids).update(is_featured=True)
    elif action == "unfeature":
        Trial.objects.filter(id__in=trial_ids).update(is_featured=False)

    log_admin_action(request.user, "bulk_action", "Trial", details={"action": action, "trial_ids": trial_ids})

    # Clear cache
    for trial_id in trial_ids:
        cache_manager.invalidate_trial_cache(trial_id)

    return Response({"message": f"{action} completed for {len(trial_ids)} trials"})


@api_view(["GET"])
@permission_classes([IsAdminUser])
def revenue_analytics(request):
    period = request.GET.get("period", "month")  # day, week, month, year

    now = timezone.now()
    if period == "day":
        start_date = now - timedelta(days=30)
        trunc_func = TruncDay
    elif period == "week":
        start_date = now - timedelta(weeks=12)
        trunc_func = TruncWeek
    elif period == "month":
        start_date = now - timedelta(days=365)
        trunc_func = TruncMonth
    else:
        start_date = now - timedelta(days=365 * 3)
        trunc_func = TruncYear

    # Revenue by period - FIXED SQL injection vulnerability
    revenue_data = (
        Subscription.objects.filter(created_at__gte=start_date)
        .annotate(period=trunc_func("created_at"))
        .values("period")
        .annotate(revenue=Sum("amount"), count=Count("id"))
        .order_by("period")
    )

    # Revenue by tier
    tier_revenue = User.objects.values("tier").annotate(
        users=Count("id"), revenue=Sum("company__subscriptions__amount")
    )

    # Top companies by revenue
    top_companies = Company.objects.annotate(total_revenue=Sum("subscriptions__amount")).order_by("-total_revenue")[:10]

    return Response(
        {
            "period_revenue": list(revenue_data),
            "tier_revenue": list(tier_revenue),
            "top_companies": CompanyAdminSerializer(top_companies, many=True).data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def system_health(request):
    health_data = {
        "database": check_database_health(),
        "cache": check_cache_health(),
        "celery": check_celery_health(),
        "storage": check_storage_health(),
    }

    overall_status = "healthy"
    for service, data in health_data.items():
        if data["status"] == "unhealthy":
            overall_status = "unhealthy"
            break
        elif data["status"] == "warning":
            overall_status = "warning"

    return Response({"overall_status": overall_status, "services": health_data, "timestamp": timezone.now()})


def check_database_health():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Get connection count
        with connection.cursor() as cursor:
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = current_database()
                """
                )
                connection_count = cursor.fetchone()[0]
            else:
                connection_count = 0

        return {"status": "healthy", "connection_count": connection_count, "response_time": "fast"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def check_cache_health():
    try:
        cache.set("health_check", "ok", 10)
        value = cache.get("health_check")

        # Get cache stats if Redis
        try:
            from django_redis import get_redis_connection

            conn = get_redis_connection("default")
            info = conn.info()
            return {
                "status": "healthy" if value == "ok" else "unhealthy",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "hit_rate": f"{info.get('keyspace_hits', 0) / max(info.get('keyspace_misses', 1), 1) * 100:.2f}%",
            }
        except Exception:
            return {"status": "healthy" if value == "ok" else "unhealthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def check_celery_health():
    try:
        from celery import current_app

        i = current_app.control.inspect()
        stats = i.stats()

        if stats:
            active_tasks = sum(len(worker.get("active", [])) for worker in stats.values())
            return {"status": "healthy", "workers": len(stats), "active_tasks": active_tasks}
        return {"status": "warning", "message": "No workers available"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def check_storage_health():
    import shutil

    try:
        usage = shutil.disk_usage("/")
        used_percent = (usage.used / usage.total) * 100

        status = "healthy"
        if used_percent > 90:
            status = "unhealthy"
        elif used_percent > 80:
            status = "warning"

        return {"status": status, "used_percent": f"{used_percent:.1f}%", "free_gb": f"{usage.free / (1024**3):.1f}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def system_config(request):
    if request.method == "GET":
        configs = SystemConfig.objects.all()
        return Response(SystemConfigSerializer(configs, many=True).data)

    key = request.data.get("key")
    value = request.data.get("value")
    description = request.data.get("description", "")

    config, created = SystemConfig.objects.update_or_create(
        key=key, defaults={"value": value, "description": description, "updated_by": request.user}
    )

    log_admin_action(request.user, "system_config", "SystemConfig", config.id, {"key": key, "value": value})

    # Clear relevant caches
    cache.delete(f"config:{key}")

    return Response(SystemConfigSerializer(config).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_activity_log(request):
    queryset = AdminAction.objects.select_related("admin")

    # Filters
    admin_id = request.GET.get("admin_id")
    if admin_id:
        queryset = queryset.filter(admin_id=admin_id)

    action_type = request.GET.get("action_type")
    if action_type:
        queryset = queryset.filter(action_type=action_type)

    date_from = request.GET.get("date_from")
    if date_from:
        queryset = queryset.filter(timestamp__gte=date_from)

    date_to = request.GET.get("date_to")
    if date_to:
        queryset = queryset.filter(timestamp__lte=date_to)

    queryset = queryset.order_by("-timestamp")

    paginator = AdminPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = AdminActionSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def generate_report(request):
    report_type = request.data.get("report_type")
    params = request.data.get("params", {})

    # Trigger async report generation
    task = generate_admin_report.delay(admin_id=request.user.id, report_type=report_type, params=params)

    return Response(
        {"task_id": task.id, "message": "Report generation started. You will receive an email when complete."}
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def export_data(request):
    export_type = request.GET.get("type")  # users, trials, companies, revenue
    format = request.GET.get("format", "csv")  # csv, xlsx

    if export_type == "users":
        queryset = User.objects.all()
        serializer_class = UserAdminSerializer
    elif export_type == "trials":
        queryset = Trial.objects.select_related("company", "industry")
        serializer_class = TrialAdminSerializer
    elif export_type == "companies":
        queryset = Company.objects.annotate(trials_count=Count("trials"))
        serializer_class = CompanyAdminSerializer
    else:
        return Response({"error": "Invalid export type"}, status=400)

    # Apply filters from query params
    # ... filter logic ...

    data = serializer_class(queryset, many=True).data

    if format == "csv":
        import csv

        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{export_type}_{timezone.now().date()}.csv"'

        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return response

    return Response({"error": "Format not supported"}, status=400)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def search_everything(request):
    query = request.GET.get("q", "")
    if len(query) < 3:
        return Response({"error": "Query too short"}, status=400)

    results = {
        "users": User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))[:5],
        "companies": Company.objects.filter(Q(name__icontains=query))[:5],
        "trials": Trial.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))[:5],
    }

    return Response(
        {
            "users": UserAdminSerializer(results["users"], many=True).data,
            "companies": CompanyAdminSerializer(results["companies"], many=True).data,
            "trials": TrialAdminSerializer(results["trials"], many=True).data,
        }
    )