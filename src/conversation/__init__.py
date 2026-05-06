"""Conversation module for dialogue handling."""
from src.conversation.detector import intent_detector, IntentDetector, Intent
from src.conversation.router import router, Router, RoutingResult
from src.conversation.context import assemble_context
from src.conversation.generator import generate_response

__all__ = [
    "intent_detector",
    "IntentDetector",
    "Intent",
    "router",
    "Router",
    "RoutingResult",
    "assemble_context",
    "generate_response",
]