"""Response generator for dialogue."""
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import create_llm
from src.conversation.context import assemble_context


SYSTEM_PROMPT = """你是一个专业的求职研究助手。你的任务是：

1. 基于用户提供的研究报告内容，回答关于公司、职位等问题
2. 如果报告中没有相关信息，明确告知用户
3. 回答要具体、实用，帮助用户准备面试
4. 如果涉及到具体数字、流程等信息，尽量引用报告中的内容

注意：只基于报告内容回答，如果报告确实没有相关信息，请明确说明。"""


async def generate_response(
    query: str,
    session_id: str,
) -> dict[str, Any]:
    """Generate a response to user query using RAG context.

    Args:
        query: User's question
        session_id: Current session ID for context retrieval

    Returns:
        Dictionary with answer and metadata
    """
    # Assemble context from session history and reports
    context = await assemble_context(query, session_id)

    if not context:
        return {
            "answer": "抱歉，我没有找到相关的研究报告内容。请先进行一项研究，然后再询问相关问题。",
            "source": None,
        }

    llm = create_llm(temperature=0.3)

    prompt = f"""上下文信息：

{context}

---

请基于以上上下文信息，回答用户的问题。如果上下文中没有相关信息，请明确说明。"""

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        return {
            "answer": response.content.strip(),
            "source": "report",
        }
    except Exception as e:
        return {
            "answer": f"生成回答时出错: {str(e)}",
            "source": None,
        }