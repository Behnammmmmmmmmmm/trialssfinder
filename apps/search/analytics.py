"""Module implementation."""
from datetime import datetime, timedelta
from typing import Any, Dict, List

from django.core.cache import cache


class SearchAnalytics:
    def __init__(self):
        self.cache_prefix = "search:analytics:"

    def track_search(self, query: str, results_count: int, filters: Dict[str, Any], user_id: int | None = None):
        """Track search query."""
        key = f"{self.cache_prefix}queries:{datetime.now().strftime('%Y%m%d')}"

        search_data = {
            "query": query,
            "results_count": results_count,
            "filters": filters,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Store in cache for batch processing
        cache_data = cache.get(key, [])
        cache_data.append(search_data)
        cache.set(key, cache_data, 86400)  # 24 hours

    def track_click(self, query: str, trial_id: int, position: int, user_id: int | None = None):
        """Track search result click."""
        key = f"{self.cache_prefix}clicks:{datetime.now().strftime('%Y%m%d')}"

        click_data = {
            "query": query,
            "trial_id": trial_id,
            "position": position,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }

        cache_data = cache.get(key, [])
        cache_data.append(click_data)
        cache.set(key, cache_data, 86400)

    def get_popular_searches(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular search queries."""
        queries = {}

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            key = f"{self.cache_prefix}queries:{date}"
            day_data = cache.get(key, [])

            for search in day_data:
                query = search["query"].lower()
                if query not in queries:
                    queries[query] = {"count": 0, "avg_results": 0}
                queries[query]["count"] += 1
                queries[query]["avg_results"] += search["results_count"]

        # Calculate averages and sort
        popular = []
        for query, data in queries.items():
            if data["count"] > 0:
                popular.append(
                    {"query": query, "count": data["count"], "avg_results": data["avg_results"] / data["count"]}
                )

        return sorted(popular, key=lambda x: x["count"], reverse=True)[:limit]

    def get_zero_result_queries(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Get queries with zero results."""
        zero_queries: dict[str, int] = {}

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            key = f"{self.cache_prefix}queries:{date}"
            day_data = cache.get(key, [])

            for search in day_data:
                if search["results_count"] == 0:
                    query = search["query"].lower()
                    zero_queries[query] = zero_queries.get(query, 0) + 1

        return [
            {"query": query, "count": count}
            for query, count in sorted(zero_queries.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]

    def get_click_through_rate(self, days: int = 7) -> Dict[str, float]:
        """Calculate CTR for search queries."""
        query_stats = {}

        # Collect search data
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")

            # Searches
            search_key = f"{self.cache_prefix}queries:{date}"
            searches = cache.get(search_key, [])
            for search in searches:
                query = search["query"].lower()
                if query not in query_stats:
                    query_stats[query] = {"searches": 0, "clicks": 0}
                query_stats[query]["searches"] += 1

            # Clicks
            click_key = f"{self.cache_prefix}clicks:{date}"
            clicks = cache.get(click_key, [])
            for click in clicks:
                query = click["query"].lower()
                if query in query_stats:
                    query_stats[query]["clicks"] += 1

        # Calculate CTR
        ctr_data = {}
        for query, stats in query_stats.items():
            if stats["searches"] > 0:
                ctr_data[query] = {
                    "ctr": stats["clicks"] / stats["searches"],
                    "searches": stats["searches"],
                    "clicks": stats["clicks"],
                }

        return ctr_data
