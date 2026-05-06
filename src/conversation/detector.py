"""Intent detection for conversation routing."""
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Intent:
    """Detected user intent."""
    type: str  # "new_research" | "followup_research" | "dialogue"
    company: Optional[str] = None
    position: Optional[str] = None
    confidence: float = 1.0


class IntentDetector:
    """Detects user intent from input."""

    # Patterns for new research requests
    NEW_RESEARCH_PATTERNS = [
        r"研究\s+(.+?)\s+(?:职位\s+)?(.+)",
        r"调研\s+(.+?)\s+(?:职位\s+)?(.+)",
        r"搜索\s+(.+?)\s+(?:职位\s+)?(.+)",
        r"帮我查\s+(.+?)\s+(?:职位\s+)?(.+)",
        r"^([^\s]+)\s+([^\s]+)$",  # Simple "公司 职位" format
    ]

    # Patterns for company comparison
    COMPARE_PATTERNS = [
        r"对比\s*(.+?)\s*(?:和|与)\s*(.+)",
        r"比较\s*(.+?)\s*(?:与)\s*(.+)",
    ]

    # Question indicators
    QUESTION_INDICATORS = ["吗", "?", "？", "怎么样", "如何", "什么", "多少", "是否"]

    def detect(
        self,
        query: str,
        company: Optional[str] = None,
        position: Optional[str] = None,
    ) -> Intent:
        """Detect intent from query and optional company/position.

        Args:
            query: User's input text
            company: Optional company from request
            position: Optional position from request

        Returns:
            Intent with type and extracted entities
        """
        query = query.strip()

        # Case 1: Explicit company + position provided → followup research
        if company and position:
            return Intent(
                type="followup_research",
                company=company,
                position=position,
            )

        # Case 2: Only company provided → check if it's a question
        if company:
            if self._is_question(query):
                return Intent(type="dialogue", company=company)
            return Intent(type="followup_research", company=company)

        # Case 3: No company/position → parse from query

        # First: Check comparison patterns (before new research patterns)
        for pattern in self.COMPARE_PATTERNS:
            match = re.search(pattern, query)
            if match:
                return Intent(
                    type="comparison",
                    company=match.group(1).strip(),
                    position=match.group(2).strip(),
                )

        # Then: Try to match new research patterns
        for pattern in self.NEW_RESEARCH_PATTERNS:
            match = re.match(pattern, query)
            if match:
                return Intent(
                    type="new_research",
                    company=match.group(1).strip(),
                    position=match.group(2).strip() if match.lastindex >= 2 else "",
                )

        # Case 5: Question without company → dialogue
        if self._is_question(query):
            return Intent(type="dialogue")

        # Default: treat as dialogue
        return Intent(type="dialogue")

    def _is_question(self, query: str) -> bool:
        """Check if query is a question."""
        # Check for question indicators
        for indicator in self.QUESTION_INDICATORS:
            if indicator in query:
                return True

        # Check for question mark
        if "?" in query or "？" in query:
            return True

        return False


# Singleton instance
intent_detector = IntentDetector()