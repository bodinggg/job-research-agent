"""Storage models for persistence."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ResearchSession:
    """A research session containing reports and conversations."""
    id: str
    company: str
    position: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime = field(default_factory=lambda: datetime.now())

    # Related entities (not stored, loaded on demand)
    report_ids: list[str] = field(default_factory=list)
    message_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "report_ids": self.report_ids,
            "message_ids": self.message_ids,
        }


@dataclass
class ResearchReport:
    """A completed research report."""
    id: str
    session_id: str
    content: str
    quality_score: float
    research_plan: list[str]  # Dimension names
    research_results: dict[str, str]  # dimension -> findings
    created_at: datetime = field(default_factory=lambda: datetime.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "quality_score": self.quality_score,
            "research_plan": self.research_plan,
            "research_results": self.research_results,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ConversationMessage:
    """A single message in the dialogue."""
    id: str
    session_id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }