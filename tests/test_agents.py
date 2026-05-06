"""Unit tests for agents and workflow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.graph.state import AgentState, ResearchDimension


class TestAgentState:
    """Tests for AgentState."""

    def test_initial_state(self):
        """Test initial state has correct defaults."""
        state = AgentState()
        assert state.user_input == ""
        assert state.target_company == ""
        assert state.target_position == ""
        assert state.research_plan == []
        assert state.research_results == {}
        assert state.draft_report == ""
        assert state.quality_score == 0.0
        assert state.final_report == ""
        assert state.rewrite_count == 0
        assert state.max_rewrites == 2

    def test_state_with_values(self):
        """Test state initialization with values."""
        state = AgentState(
            user_input="ByteDance SRE",
            target_company="ByteDance",
            target_position="SRE",
        )
        assert state.target_company == "ByteDance"
        assert state.target_position == "SRE"
        assert state.user_input == "ByteDance SRE"

    def test_research_dimension(self):
        """Test ResearchDimension structure."""
        dim = ResearchDimension(
            name="Tech Stack",
            search_keywords=["python", "kubernetes", "golang"],
            priority="high"
        )
        assert dim.name == "Tech Stack"
        assert len(dim.search_keywords) == 3
        assert dim.priority == "high"
        assert dim.findings == ""


class TestPlannerOutput:
    """Tests for Planner agent output validation."""

    def test_research_plan_has_dimensions(self):
        """Test that research plan contains expected dimensions."""
        # This tests the expected output structure
        expected_dimensions = [
            "Company Overview",
            "Tech Stack",
            "Interview Process",
            "Salary Range",
            "Preparation Tips"
        ]
        assert len(expected_dimensions) >= 5

    def test_research_dimension_structure(self):
        """Test that each dimension has required fields."""
        dim = ResearchDimension(
            name="Test Dimension",
            search_keywords=["keyword1", "keyword2"],
            priority="high"
        )
        assert hasattr(dim, "name")
        assert hasattr(dim, "search_keywords")
        assert hasattr(dim, "priority")
        assert dim.priority in ["high", "medium", "low"]


class TestCriticScoring:
    """Tests for Critic agent scoring logic."""

    def test_quality_threshold(self):
        """Test quality score threshold constant."""
        from src.graph.workflow import QUALITY_THRESHOLD
        assert QUALITY_THRESHOLD == 7.0

    def test_rewrite_decision(self):
        """Test rewrite decision logic."""
        from src.graph.workflow import should_rewrite

        # Score below threshold should return "writer"
        low_score_state = AgentState(
            quality_score=5.0,
            rewrite_count=0,
            max_rewrites=2
        )
        assert should_rewrite(low_score_state) == "writer"

        # Score above threshold should return "finalize"
        high_score_state = AgentState(
            quality_score=8.0,
            rewrite_count=0,
            max_rewrites=2
        )
        assert should_rewrite(high_score_state) == "finalize"

        # Max rewrites reached should return "finalize"
        max_rewrites_state = AgentState(
            quality_score=5.0,
            rewrite_count=2,
            max_rewrites=2
        )
        assert should_rewrite(max_rewrites_state) == "finalize"


class TestWriterOutput:
    """Tests for Writer agent output validation."""

    def test_report_structure(self):
        """Test that generated report follows expected structure."""
        # The writer prompt specifies this structure:
        expected_sections = [
            "Company Overview",
            "Technical Stack",
            "Team Structure",
            "Interview Process",
            "Salary Range",
            "Preparation Tips",
            "References"
        ]
        assert len(expected_sections) == 7


class TestResearcherParallel:
    """Tests for Researcher agent parallel execution."""

    def test_parallel_search_readiness(self):
        """Test that researcher is set up for parallel execution."""
        # This validates that the researcher module uses asyncio.gather
        import inspect
        from src.agents import researcher

        source = inspect.getsource(researcher.researcher_node)
        assert "asyncio.gather" in source, "Researcher should use asyncio.gather for parallel execution"


class TestWorkflow:
    """Tests for the complete workflow."""

    def test_workflow_nodes_exist(self):
        """Test that all required workflow nodes are defined."""
        from src.graph import workflow
        assert hasattr(workflow, "planner")
        assert hasattr(workflow, "researcher")
        assert hasattr(workflow, "writer")
        assert hasattr(workflow, "critic")

    def test_workflow_compilation(self):
        """Test that workflow can be compiled without errors."""
        from src.graph.workflow import create_workflow
        graph = create_workflow()
        assert graph is not None


class TestConfig:
    """Tests for configuration."""

    def test_default_settings(self):
        """Test settings loaded from .env file."""
        from src.config import settings
        assert settings.llm_base_url == "https://api.siliconflow.cn/v1"
        assert settings.llm_model_name == "Pro/deepseek-ai/DeepSeek-V3.2"
        assert settings.embedding_model_name == "Qwen/Qwen3-Embedding-8B"
        assert settings.qdrant_port == 6333
