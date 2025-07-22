import json

# Existing schedules...

# Cache warming every 30 minutes
cache_interval, _ = IntervalSchedule.objects.get_or_create(
    every=30,
    period=IntervalSchedule.MINUTES,
)

PeriodicTask.objects.get_or_create(
    interval=cache_interval,
    name="Warm critical caches",
    task="apps.core.cache_warming.warm_cache",
)

# Clear stale caches every 2 hours
stale_cache_interval, _ = IntervalSchedule.objects.get_or_create(
    every=2,
    period=IntervalSchedule.HOURS,
)

PeriodicTask.objects.get_or_create(
    interval=stale_cache_interval,
    name="Clear stale caches",
    task="apps.core.cache_warming.invalidate_stale_caches",
)
