"""Search module for multi-platform job search."""
from src.search.models import JobSummary, SearchResult
from src.search.crawler import search_jobs

__all__ = ["JobSummary", "SearchResult", "search_jobs"]
