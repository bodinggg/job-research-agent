"""LangGraph state definitions."""
from dataclasses import dataclass, field
from typing import Annotated
import operator


@dataclass
class ResearchDimension:
    """A single research dimension."""
    name: str
    search_keywords: list[str]
    priority: str  # "high", "medium", "low"
    findings: str = ""


@dataclass
class AgentState:
    """State shared across all agents in the research workflow."""

    # User input
    user_input: str = ""
    target_company: str = ""
    target_position: str = ""

    # Agent outputs
    research_plan: list[ResearchDimension] = field(default_factory=list)
    research_results: dict[str, str] = field(default_factory=dict)
    draft_report: str = ""
    quality_score: float = 0.0
    revision_suggestions: str = ""
    final_report: str = ""

    # Workflow control
    rewrite_count: int = 0
    max_rewrites: int = 2
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def divide_messages(left: list[str], right: list[str]) -> list[str]:
    """Concatenate two message lists."""
    return left + right


# Annotated state with reducers for list fields
class AgentStateAnnotated(AgentState):
    """AgentState with reducers for LangGraph compatibility."""

    messages: Annotated[list[str], operator.add] = field(default_factory=list)
    errors: Annotated[list[str], operator.add] = field(default_factory=list)
