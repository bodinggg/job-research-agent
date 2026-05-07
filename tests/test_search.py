"""Tests for search module."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.search.models import JobSummary, SearchResult


class TestJobSummary:
    """Tests for JobSummary model."""

    def test_job_summary_creation(self):
        """Test creating a JobSummary instance."""
        job = JobSummary(
            source="boss",
            title="高级后端工程师",
            company="字节跳动",
            salary="30-50K",
            address="北京",
            tags=["Python", "Go"],
            job_url="https://www.zhipin.com/job/123",
        )

        assert job.source == "boss"
        assert job.title == "高级后端工程师"
        assert job.company == "字节跳动"
        assert job.salary == "30-50K"
        assert job.address == "北京"
        assert job.tags == ["Python", "Go"]
        assert job.job_url == "https://www.zhipin.com/job/123"

    def test_job_summary_optional_fields(self):
        """Test JobSummary with optional fields."""
        job = JobSummary(
            source="liepin",
            title="前端工程师",
            company="腾讯",
        )

        assert job.source == "liepin"
        assert job.title == "前端工程师"
        assert job.company == "腾讯"
        assert job.salary is None
        assert job.address is None
        assert job.tags == []
        assert job.job_url is None


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_search_result_creation(self):
        """Test creating a SearchResult instance."""
        jobs = [
            JobSummary(source="boss", title="工程师", company="公司A"),
            JobSummary(source="liepin", title="设计师", company="公司B"),
        ]
        result = SearchResult(jobs=jobs, total=2, query="后端")

        assert len(result.jobs) == 2
        assert result.total == 2
        assert result.query == "后端"

    def test_search_result_empty(self):
        """Test SearchResult with no jobs."""
        result = SearchResult(jobs=[], total=0, query="不存在")

        assert result.jobs == []
        assert result.total == 0
        assert result.query == "不存在"


class TestSearchEngines:
    """Tests for search engine implementations."""

    @pytest.mark.asyncio
    @patch("src.search.engines.boss.BossEngine.search")
    async def test_boss_engine_search(self, mock_search):
        """Test Boss search engine."""
        from src.search.engines.boss import BossEngine

        mock_search.return_value = [
            JobSummary(
                source="boss",
                title="Python工程师",
                company="美团",
                salary="25-40K",
                address="北京",
            )
        ]

        engine = BossEngine()
        results = await engine.search("Python工程师", city="北京")

        assert len(results) == 1
        assert results[0].source == "boss"
        assert results[0].company == "美团"
        mock_search.assert_called_once_with("Python工程师", city="北京")

    @pytest.mark.asyncio
    @patch("src.search.engines.liepin.LiepinEngine.search")
    async def test_liepin_engine_search(self, mock_search):
        """Test Liepin search engine."""
        from src.search.engines.liepin import LiepinEngine

        mock_search.return_value = [
            JobSummary(
                source="liepin",
                title="算法工程师",
                company="字节跳动",
                salary="40-60K",
                address="上海",
            )
        ]

        engine = LiepinEngine()
        results = await engine.search("算法工程师")

        assert len(results) == 1
        assert results[0].source == "liepin"
        assert results[0].company == "字节跳动"


class TestSearchJobs:
    """Tests for unified search_jobs function."""

    @pytest.mark.asyncio
    @patch("src.search.crawler.BossEngine.search")
    @patch("src.search.crawler.LiepinEngine.search")
    async def test_search_jobs_multi_engine(self, mock_liepin, mock_boss):
        """Test searching across multiple engines."""
        from src.search.crawler import search_jobs

        mock_boss.return_value = [
            JobSummary(source="boss", title="工程师", company="公司A")
        ]
        mock_liepin.return_value = [
            JobSummary(source="liepin", title="工程师", company="公司B")
        ]

        results = await search_jobs("工程师", sites=["boss", "liepin"])

        assert len(results) == 2
        assert results[0].source == "boss"
        assert results[1].source == "liepin"

    @pytest.mark.asyncio
    @patch("src.search.crawler.BossEngine.search")
    async def test_search_jobs_single_engine(self, mock_boss):
        """Test searching with single engine."""
        from src.search.crawler import search_jobs

        mock_boss.return_value = [
            JobSummary(source="boss", title="前端", company="公司C")
        ]

        results = await search_jobs("前端", sites=["boss"])

        assert len(results) == 1
        assert results[0].source == "boss"

    @pytest.mark.asyncio
    @patch("src.search.crawler.BossEngine.search")
    async def test_search_jobs_no_results(self, mock_boss):
        """Test search with no results."""
        from src.search.crawler import search_jobs

        mock_boss.return_value = []

        results = await search_jobs("不存在的职位", sites=["boss"])

        assert len(results) == 0


class TestSearchAPI:
    """Tests for search API endpoint."""

    @pytest.mark.asyncio
    @patch("src.api.main.search_jobs")
    async def test_search_endpoint(self, mock_search):
        """Test POST /search endpoint."""
        from src.api.main import SearchRequest, SearchResponse

        mock_search.return_value = [
            JobSummary(
                source="liepin",
                title="Python工程师",
                company="字节跳动",
                salary="40-60K",
                address="北京",
            )
        ]

        request = SearchRequest(query="Python工程师", sites=["liepin"], city="北京")
        jobs = await mock_search(query="Python工程师", sites=["liepin"], city="北京")
        response = SearchResponse(jobs=jobs, total=len(jobs), query=request.query)

        assert response.total == 1
        assert response.jobs[0].title == "Python工程师"
        assert response.query == "Python工程师"
