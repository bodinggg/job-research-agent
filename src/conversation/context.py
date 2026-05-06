"""Context assembler for RAG-based dialogue."""
from typing import Optional

from src.storage import report_repo, message_repo
from src.storage.qdrant_client import get_qdrant_client


async def assemble_context(
    query: str,
    session_id: str,
    top_k: int = 5,
) -> str:
    """Assemble context for dialogue from session history and reports using RAG.

    Args:
        query: User's question
        session_id: Current session ID
        top_k: Number of report chunks to retrieve

    Returns:
        Formatted context string for LLM
    """
    parts = []

    # 1. Get recent conversation history
    messages = message_repo.list_by_session(session_id, limit=10)
    if messages:
        history_lines = []
        for msg in messages[-6:]:  # Last 6 messages
            role_label = "用户" if msg.role == "user" else "助手"
            history_lines.append(f"- {role_label}: {msg.content}")
        parts.append("当前会话历史:\n" + "\n".join(history_lines))

    # 2. Get relevant report chunks using RAG
    try:
        qdrant_client = get_qdrant_client()
        search_results = await qdrant_client.search(
            query=query,
            session_id=session_id,
            top_k=top_k,
        )

        if search_results:
            # Format retrieved chunks with scores
            chunks_text = []
            for i, result in enumerate(search_results, 1):
                chunks_text.append(
                    f"[相关段落{i}]({result['score']:.2f}): {result['content']}"
                )
            parts.append("相关报告内容:\n" + "\n\n".join(chunks_text))
        else:
            # Fallback to full report if no RAG results
            report = report_repo.get_latest(session_id)
            if report:
                parts.append(f"研究报告内容:\n{report.content}")
    except Exception:
        # If RAG fails, fall back to full report
        report = report_repo.get_latest(session_id)
        if report:
            parts.append(f"研究报告内容:\n{report.content}")

    # 3. Add user query
    parts.append(f"用户问题: {query}")

    return "\n\n".join(parts)


def format_messages_for_context(messages: list) -> str:
    """Format messages for context string."""
    if not messages:
        return ""

    lines = []
    for msg in messages:
        role = "用户" if msg.role == "user" else "助手"
        lines.append(f"- {role}: {msg.content}")

    return "\n".join(lines) if lines else ""