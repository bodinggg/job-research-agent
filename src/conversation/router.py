"""Request routing for research vs dialogue."""
from dataclasses import dataclass
from typing import Optional
from src.conversation.detector import Intent, intent_detector


@dataclass
class RoutingResult:
    """Result of routing decision."""
    route: str  # "research" | "dialogue"
    intent: Intent
    session_id: Optional[str] = None


class Router:
    """Routes requests to appropriate handlers."""

    def __init__(self):
        self.detector = intent_detector

    async def route(
        self,
        query: str,
        session_id: Optional[str] = None,
        company: Optional[str] = None,
        position: Optional[str] = None,
    ) -> RoutingResult:
        """Route request based on intent.

        Args:
            query: User's input text
            session_id: Optional existing session ID
            company: Optional company from request
            position: Optional position from request

        Returns:
            RoutingResult with route and intent
        """
        intent = self.detector.detect(query, company, position)

        # Determine route based on intent type
        if intent.type in ("new_research", "followup_research", "comparison"):
            return RoutingResult(
                route="research",
                intent=intent,
                session_id=session_id,
            )
        else:  # dialogue
            return RoutingResult(
                route="dialogue",
                intent=intent,
                session_id=session_id,
            )


# Singleton instance
router = Router()