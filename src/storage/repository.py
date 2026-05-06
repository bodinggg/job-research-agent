"""Repository for storage operations."""
import uuid
from datetime import datetime
from typing import Optional
from src.storage.models import ResearchSession, ResearchReport, ConversationMessage


class SessionRepository:
    """Repository for research sessions."""

    def __init__(self):
        self._sessions: dict[str, ResearchSession] = {}

    def create(self, company: str, position: str) -> ResearchSession:
        """Create a new session."""
        session = ResearchSession(
            id=str(uuid.uuid4()),
            company=company,
            position=position,
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[ResearchSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def list_all(self) -> list[ResearchSession]:
        """List all sessions."""
        return list(self._sessions.values())

    def update(self, session: ResearchSession) -> ResearchSession:
        """Update session."""
        session.updated_at = datetime.now()
        self._sessions[session.id] = session
        return session

    def add_report(self, session_id: str, report_id: str) -> bool:
        """Add report ID to session."""
        session = self._sessions.get(session_id)
        if session:
            if report_id not in session.report_ids:
                session.report_ids.append(report_id)
            return True
        return False

    def add_message(self, session_id: str, message_id: str) -> bool:
        """Add message ID to session."""
        session = self._sessions.get(session_id)
        if session:
            if message_id not in session.message_ids:
                session.message_ids.append(message_id)
            return True
        return False


class ReportRepository:
    """Repository for research reports."""

    def __init__(self):
        self._reports: dict[str, ResearchReport] = {}

    def create(
        self,
        session_id: str,
        content: str,
        quality_score: float,
        research_plan: list[str],
        research_results: dict[str, str],
    ) -> ResearchReport:
        """Create a new report."""
        report = ResearchReport(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=content,
            quality_score=quality_score,
            research_plan=research_plan,
            research_results=research_results,
        )
        self._reports[report.id] = report
        return report

    def get(self, report_id: str) -> Optional[ResearchReport]:
        """Get report by ID."""
        return self._reports.get(report_id)

    def list_by_session(self, session_id: str) -> list[ResearchReport]:
        """List all reports for a session."""
        return [
            r for r in self._reports.values()
            if r.session_id == session_id
        ]

    def get_latest(self, session_id: str) -> Optional[ResearchReport]:
        """Get latest report for a session."""
        reports = self.list_by_session(session_id)
        if not reports:
            return None
        return max(reports, key=lambda r: r.created_at)


class MessageRepository:
    """Repository for conversation messages."""

    def __init__(self):
        self._messages: dict[str, ConversationMessage] = {}

    def create(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> ConversationMessage:
        """Create a new message."""
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
        )
        self._messages[message.id] = message
        return message

    def get(self, message_id: str) -> Optional[ConversationMessage]:
        """Get message by ID."""
        return self._messages.get(message_id)

    def list_by_session(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> list[ConversationMessage]:
        """List all messages for a session, ordered by creation time."""
        messages = [
            m for m in self._messages.values()
            if m.session_id == session_id
        ]
        messages.sort(key=lambda m: m.created_at)
        if limit:
            messages = messages[-limit:]
        return messages


# Singleton instances for in-memory storage
session_repo = SessionRepository()
report_repo = ReportRepository()
message_repo = MessageRepository()