"""Module implementation."""
import logging
from typing import Any, Dict, List

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logger = logging.getLogger("trialssfinder.search")


class ElasticsearchBackend:
    def __init__(self):
        es_config = {
            "hosts": [settings.ELASTICSEARCH_URL],
            "verify_certs": False,  # Set to True in production with proper certs
            "ssl_show_warn": False,
        }

        if settings.ELASTICSEARCH_USER and settings.ELASTICSEARCH_PASSWORD:
            es_config["basic_auth"] = (settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)

        self.client = Elasticsearch(**es_config)
        self.index_name = settings.ELASTICSEARCH_INDEX

    def create_index(self):
        """Create index with proper mappings."""
        if self.client.indices.exists(index=self.index_name):
            return

        mappings = {
            "properties": {
                "id": {"type": "integer"},
                "title": {
                    "type": "text",
                    "analyzer": "english",
                    "fields": {"keyword": {"type": "keyword"}, "suggest": {"type": "completion", "analyzer": "simple"}},
                },
                "description": {"type": "text", "analyzer": "english"},
                "industry": {"type": "keyword"},
                "industry_id": {"type": "integer"},
                "location": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "company_name": {"type": "keyword"},
                "company_id": {"type": "integer"},
                "start_date": {"type": "date"},
                "end_date": {"type": "date"},
                "is_featured": {"type": "boolean"},
                "status": {"type": "keyword"},
                "created_at": {"type": "date"},
                "tags": {"type": "keyword"},
                "price_range": {"type": "integer_range"},
                "relevance_score": {"type": "float"},
            }
        }

        settings_config = {
            "analysis": {
                "analyzer": {
                    "autocomplete": {"tokenizer": "autocomplete", "filter": ["lowercase"]},
                    "autocomplete_search": {"tokenizer": "lowercase"},
                },
                "tokenizer": {
                    "autocomplete": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 10,
                        "token_chars": ["letter", "digit"],
                    }
                },
            }
        }

        self.client.indices.create(index=self.index_name, mappings=mappings, settings=settings_config)

    def index_trial(self, trial: Dict[str, Any]):
        """Index a single trial."""
        self.client.index(index=self.index_name, id=trial["id"], document=trial)

    def bulk_index_trials(self, trials: List[Dict[str, Any]]):
        """Bulk index trials."""
        actions = [{"_index": self.index_name, "_id": trial["id"], "_source": trial} for trial in trials]
        bulk(self.client, actions)

    def search(
        self, query: str, filters: Dict[str, Any], page: int = 1, size: int = 20, sort_by: str = "_score"
    ) -> Dict[str, Any]:
        """Advanced search with facets."""
        from_index = (page - 1) * size

        # Build query
        must_clauses = []

        if query:
            must_clauses.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description^2", "industry", "company_name", "location"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )

        # Apply filters
        filter_clauses = [{"term": {"status": "approved"}}]

        if filters.get("industry"):
            filter_clauses.append({"term": {"industry_id": filters["industry"]}})

        if filters.get("location"):
            filter_clauses.append({"match": {"location": {"query": filters["location"], "fuzziness": "AUTO"}}})

        if filters.get("is_featured") is not None:
            filter_clauses.append({"term": {"is_featured": filters["is_featured"]}})

        if filters.get("date_range"):
            filter_clauses.append(
                {"range": {"start_date": {"gte": filters["date_range"]["start"], "lte": filters["date_range"]["end"]}}}
            )

        # Build aggregations for facets
        aggs = {
            "industries": {"terms": {"field": "industry", "size": 50}}  # type: ignore,
            "locations": {"terms": {"field": "location.keyword", "size": 50}},
            "companies": {"terms": {"field": "company_name", "size": 20}},
            "date_histogram": {"date_histogram"  # type: ignore: {"field": "created_at", "calendar_interval": "month"}},
        }

        # Execute search
        body = {
            "query": {
                "bool": {"must": must_clauses if must_clauses else [{"match_all": {}}], "filter": filter_clauses}
            },
            "aggs": aggs,
            "from": from_index,
            "size": size,
            "highlight": {"fields": {"title": {}, "description": {"fragment_size": 150}}},
        }

        # Add sorting
        if sort_by == "relevance":
            body["sort"] = [{"_score": "desc"}]
        elif sort_by == "date":
            body["sort"] = [{"created_at": "desc"}]
        elif sort_by == "featured":
            body["sort"] = [{"is_featured": "desc"}, {"_score": "desc"}]

        result = self.client.search(index=self.index_name, body=body)

        # Format response
        return {
            "total": result["hits"]["total"]["value"],
            "results": [self._format_hit(hit) for hit in result["hits"]["hits"]],
            "facets": self._format_aggregations(result.get("aggregations", {})),
            "page": page,
            "size": size,
        }

    def suggest(self, prefix: str, size: int = 5) -> List[str]:
        """Autocomplete suggestions."""
        body = {
            "suggest": {
                "trial-suggest": {
                    "prefix": prefix,
                    "completion": {"field": "title.suggest", "size": size, "skip_duplicates": True},
                }
            }
        }

        result = self.client.search(index=self.index_name, body=body)
        suggestions = []

        for suggestion in result.get("suggest", {}).get("trial-suggest", []):
            for option in suggestion.get("options", []):
                suggestions.append(option["text"])

        return suggestions

    def _format_hit(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """Format search hit."""
        source = hit["_source"]
        formatted = {
            "id": source["id"],
            "title": source["title"],
            "description": source["description"],
            "industry": source["industry"],
            "location": source["location"],
            "company_name": source["company_name"],
            "is_featured": source.get("is_featured", False),
            "score": hit["_score"],
        }

        # Add highlights if available
        if "highlight" in hit:
            formatted["highlights"] = hit["highlight"]

        return formatted

    def _format_aggregations(self, aggs: Dict[str, Any]) -> Dict[str, Any]:
        """Format aggregations for frontend."""
        facets = {}

        if "industries" in aggs:
            facets["industries"] = [
                {"key": bucket["key"], "count": bucket["doc_count"]} for bucket in aggs["industries"]["buckets"]
            ]

        if "locations" in aggs:
            facets["locations"] = [
                {"key": bucket["key"], "count": bucket["doc_count"]} for bucket in aggs["locations"]["buckets"]
            ]

        if "companies" in aggs:
            facets["companies"] = [
                {"key": bucket["key"], "count": bucket["doc_count"]} for bucket in aggs["companies"]["buckets"]
            ]

        return facets
