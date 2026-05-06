"""Tests for conversation module."""
import pytest
from src.conversation.detector import IntentDetector, Intent


class TestIntentDetector:
    """Tests for IntentDetector."""

    def setup_method(self):
        self.detector = IntentDetector()

    def test_detect_new_research_simple(self):
        """Test detecting simple new research request."""
        intent = self.detector.detect("字节跳动 后端工程师")
        assert intent.type == "new_research"
        assert intent.company == "字节跳动"
        assert intent.position == "后端工程师"

    def test_detect_new_research_with_prefix(self):
        """Test detecting research with prefix."""
        intent = self.detector.detect("研究 字节跳动 后端工程师")
        assert intent.type == "new_research"
        assert intent.company == "字节跳动"

    def test_detect_dialogue_question(self):
        """Test detecting dialogue question."""
        intent = self.detector.detect("技术栈是什么？")
        assert intent.type == "dialogue"

    def test_detect_dialogue_with_company(self):
        """Test detecting dialogue when company is provided separately."""
        intent = self.detector.detect("加班严重吗？", company="字节跳动")
        assert intent.type == "dialogue"
        assert intent.company == "字节跳动"

    def test_detect_followup_with_company_position(self):
        """Test detecting followup research with company and position."""
        intent = self.detector.detect("再研究一下", company="腾讯", position="前端")
        assert intent.type == "followup_research"
        assert intent.company == "腾讯"
        assert intent.position == "前端"

    def test_detect_comparison(self):
        """Test detecting comparison request."""
        intent = self.detector.detect("对比字节跳动和腾讯")
        assert intent.type == "comparison"

    def test_detect_question_markers(self):
        """Test question marker detection."""
        # Chinese question markers
        assert self.detector._is_question("这样可以吗")
        assert self.detector._is_question("怎么样")
        assert self.detector._is_question("如何")
        # English question mark
        assert self.detector._is_question("Is it good?")
        # Chinese question mark
        assert self.detector._is_question("好吗？")


class TestIntent:
    """Tests for Intent dataclass."""

    def test_intent_creation(self):
        """Test Intent creation."""
        intent = Intent(type="dialogue", company="字节跳动", confidence=0.9)
        assert intent.type == "dialogue"
        assert intent.company == "字节跳动"
        assert intent.confidence == 0.9

    def test_intent_defaults(self):
        """Test Intent default values."""
        intent = Intent(type="dialogue")
        assert intent.company is None
        assert intent.position is None
        assert intent.confidence == 1.0