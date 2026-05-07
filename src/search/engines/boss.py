"""Boss直聘 search engine."""
import httpx
from typing import Optional

from src.search.models import JobSummary


class BossEngine:
    """Search engine for Boss直聘 (zhipin.com)."""

    BASE_URL = "https://www.zhipin.com/webapi/zpboss/search/job.json"

    async def search(
        self,
        keyword: str,
        city: Optional[str] = None,
        salary: Optional[str] = None,
        **kwargs
    ) -> list[JobSummary]:
        """Search jobs on Boss直聘.

        Args:
            keyword: Search keyword
            city: City name
            salary: Salary range
            **kwargs: Additional parameters

        Returns:
            List of job summaries
        """
        params = {
            "query": keyword,
            "page": 1,
            "pageSize": 20,
        }
        if city:
            params["city"] = city
        if salary:
            params["salary"] = salary

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_response(data)
        except Exception:
            pass

        return []

    def _parse_response(self, data: dict) -> list[JobSummary]:
        """Parse Boss API response."""
        jobs = []
        if data.get("zpData"):
            for item in data["zpData"].get("jobList", []):
                jobs.append(
                    JobSummary(
                        source="boss",
                        title=item.get("jobName", ""),
                        company=item.get("companyName", ""),
                        salary=item.get("salary", ""),
                        address=item.get("cityName", ""),
                        tags=item.get("skills", []),
                        job_url=f"https://www.zhipin.com/job_detail/{item.get('hashedJobId', '')}",
                    )
                )
        return jobs
