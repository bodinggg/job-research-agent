"""Unified job search crawler across multiple platforms."""
from typing import Optional

from src.search.models import JobSummary
from src.search.engines.boss import BossEngine
from src.search.engines.liepin import LiepinEngine


async def search_jobs(
    query: str,
    sites: list[str] = None,
    city: Optional[str] = None,
    salary: Optional[str] = None,
    **kwargs
) -> list[JobSummary]:
    """Search jobs across multiple platforms.

    Args:
        query: Search query (e.g., "Python工程师")
        sites: List of sites to search (default: ["boss", "liepin"])
        city: City filter
        salary: Salary range filter
        **kwargs: Additional parameters

    Returns:
        List of job summaries from all platforms
    """
    if sites is None:
        sites = ["boss", "liepin"]

    results = []

    engines = {
        "boss": BossEngine(),
        "liepin": LiepinEngine(),
    }

    for site in sites:
        if site in engines:
            try:
                jobs = await engines[site].search(
                    keyword=query,
                    city=city,
                    salary=salary,
                    **kwargs
                )
                results.extend(jobs)
            except Exception:
                pass

    return results
