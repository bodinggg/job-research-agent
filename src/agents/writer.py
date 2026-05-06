"""Writer Agent - generates structured research reports."""
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import create_llm
from src.graph.state import AgentState
from src.think_log import log_think


WRITER_SYSTEM_PROMPT = """你是一位专业的求职研究报告撰写专家。你的任务是将研究发现综合成一份全面、结构化的Markdown报告。

严格遵循以下结构：
1. 公司概况
2. 技术栈与工程文化
3. 团队结构与成长机会
4. 面试流程与阶段
5. 薪资范围与福利（如有）
6. 准备建议与推荐
7. 参考来源

使用Markdown格式以提高可读性。尽可能包含具体的细节、数字和实例。"""


WRITER_USER_PROMPT = """为以下职位撰写一份全面的研究报告：

公司：{company}
职位：{position}

研究发现：
{research_results}

根据以上研究发现，撰写一份遵循指定结构的详细Markdown报告。
如果某些信息不可用，请明确说明，但仍然提供你能找到的内容。
要具体且真实。尽可能包含数字、技术和流程细节。"""


def format_research_results(results: dict[str, str]) -> str:
    """Format research results into a readable string."""
    formatted = []
    for dimension, findings in results.items():
        formatted.append(f"## {dimension}\n{findings}\n")
    return "\n".join(formatted)


async def writer_node(state: AgentState) -> dict[str, Any]:
    """Generate structured research report from research findings.

    Args:
        state: Current workflow state with research_results

    Returns:
        Updated state with draft_report
    """
    if not state.research_results:
        return {
            "errors": ["没有可用的研究成果"],
            "draft_report": ""
        }

    llm = create_llm(temperature=0.3)

    # Format research results
    results_text = format_research_results(state.research_results)

    # Format prompt
    user_prompt = WRITER_USER_PROMPT.format(
        company=state.target_company,
        position=state.target_position,
        research_results=results_text
    )

    try:
        response = await llm.ainvoke([
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])

        draft_report = response.content.strip()

        # Log the thinking process
        log_think("writer", "writing", user_prompt, draft_report, {
            "company": state.target_company,
            "position": state.target_position,
            "research_dimensions": list(state.research_results.keys())
        })

        return {
            "draft_report": draft_report,
            "messages": [f"作者: 生成了报告 ({len(draft_report)} 字符)"]
        }

    except Exception as e:
        return {
            "errors": [f"作者错误: {str(e)}"],
            "draft_report": ""
        }
