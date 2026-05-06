"""Tests for storage module."""
import pytest
from datetime import datetime
from src.storage.models import ResearchSession, ResearchReport, ConversationMessage
from src.storage.repository import SessionRepository, ReportRepository, MessageRepository


class TestResearchSession:
    def test_create_session(self):
        """Test session creation."""
        session = ResearchSession(
            id="test-id",
            company="字节跳动",
            position="后端工程师",
        )
        assert session.id == "test-id"
        assert session.company == "字节跳动"
        assert session.position == "后端工程师"
        assert isinstance(session.created_at, datetime)

    def test_session_to_dict(self):
        """Test session serialization."""
        session = ResearchSession(
            id="test-id",
            company="字节跳动",
            position="后端工程师",
        )
        d = session.to_dict()
        assert d["id"] == "test-id"
        assert d["company"] == "字节跳动"
        assert d["position"] == "后端工程师"
        assert "created_at" in d


class TestResearchReport:
    def test_create_report(self):
        """Test report creation."""
        report = ResearchReport(
            id="report-id",
            session_id="session-id",
            content="# 字节跳动研究报告",
            quality_score=8.5,
            research_plan=["公司概况", "技术栈"],
            research_results={"公司概况": "成立于2012年"},
        )
        assert report.id == "report-id"
        assert report.session_id == "session-id"
        assert report.quality_score == 8.5

    def test_report_to_dict(self):
        """Test report serialization."""
        report = ResearchReport(
            id="report-id",
            session_id="session-id",
            content="报告内容",
            quality_score=8.0,
            research_plan=["技术栈"],
            research_results={"技术栈": "Go, Java"},
        )
        d = report.to_dict()
        assert d["id"] == "report-id"
        assert d["quality_score"] == 8.0
        assert d["research_plan"] == ["技术栈"]


class TestConversationMessage:
    def test_create_message(self):
        """Test message creation."""
        msg = ConversationMessage(
            id="msg-id",
            session_id="session-id",
            role="user",
            content="技术栈是什么？",
        )
        assert msg.id == "msg-id"
        assert msg.role == "user"
        assert msg.content == "技术栈是什么？"

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = ConversationMessage(
            id="msg-id",
            session_id="session-id",
            role="assistant",
            content="主要使用Go和Java",
        )
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert "created_at" in d


class TestSessionRepository:
    def test_create_and_get(self):
        """Test session CRUD."""
        repo = SessionRepository()
        session = repo.create("腾讯", "前端工程师")
        assert session.company == "腾讯"
        assert session.position == "前端工程师"

        retrieved = repo.get(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id

    def test_get_nonexistent(self):
        """Test getting non-existent session."""
        repo = SessionRepository()
        result = repo.get("nonexistent-id")
        assert result is None

    def test_add_report_to_session(self):
        """Test adding report to session."""
        repo = SessionRepository()
        session = repo.create("腾讯", "前端工程师")

        result = repo.add_report(session.id, "report-1")
        assert result is True

        updated = repo.get(session.id)
        assert "report-1" in updated.report_ids


class TestReportRepository:
    def test_create_and_get(self):
        """Test report CRUD."""
        repo = ReportRepository()
        report = repo.create(
            session_id="session-1",
            content="# 测试报告",
            quality_score=8.0,
            research_plan=["公司概况"],
            research_results={"公司概况": "知名公司"},
        )
        assert report.session_id == "session-1"

        retrieved = repo.get(report.id)
        assert retrieved is not None
        assert retrieved.content == "# 测试报告"

    def test_list_by_session(self):
        """Test listing reports by session."""
        repo = ReportRepository()
        repo.create("session-1", "报告1", 7.0, [], {})
        repo.create("session-1", "报告2", 8.0, [], {})
        repo.create("session-2", "报告3", 7.5, [], {})

        session1_reports = repo.list_by_session("session-1")
        assert len(session1_reports) == 2

    def test_get_latest(self):
        """Test getting latest report by creation time."""
        repo = ReportRepository()
        r1 = repo.create("session-1", "报告1", 7.0, [], {})

        import time
        time.sleep(0.01)  # Ensure different timestamps

        r2 = repo.create("session-1", "报告2", 8.0, [], {})
        latest = repo.get_latest("session-1")
        assert latest.id == r2.id


class TestMessageRepository:
    def test_create_and_get(self):
        """Test message CRUD."""
        repo = MessageRepository()
        msg = repo.create("session-1", "user", "你好")
        assert msg.role == "user"

        retrieved = repo.get(msg.id)
        assert retrieved is not None
        assert retrieved.content == "你好"

    def test_list_by_session(self):
        """Test listing messages by session."""
        repo = MessageRepository()
        repo.create("session-1", "user", "问题1")
        repo.create("session-1", "assistant", "回答1")
        repo.create("session-1", "user", "问题2")

        messages = repo.list_by_session("session-1")
        assert len(messages) == 3

    def test_list_with_limit(self):
        """Test message list with limit."""
        repo = MessageRepository()
        for i in range(5):
            repo.create("session-1", "user", f"消息{i}")

        recent = repo.list_by_session("session-1", limit=3)
        assert len(recent) == 3