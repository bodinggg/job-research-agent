"""Critic Agent - evaluates report quality and provides revision suggestions."""
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import create_llm
from src.graph.state import AgentState
from src.think_log import log_think
import json


CRITIC_SYSTEM_PROMPT = """你是一位专业的求职研究报告质量评审专家。你的任务是评估研究报告的完整性、准确性和实用性。

评估标准：
1. 完整性 - 是否涵盖了所有关键领域？（公司概况、技术栈、面试流程等）
2. 准确性 - 信息是否真实且有来源？
3. 实用性 - 这能帮助求职者准备面试吗？
4. 具体性 - 是否有具体的细节、数字和示例？

评分标准：将报告评为0-10分：
- 9-10分：优秀，全面，非常有帮助
- 7-8分：良好，涵盖了最重要的领域
- 5-6分：一般，缺少一些关键信息
- 3-4分：低于平均，存在明显差距
- 0-2分：较差，对面试准备没有帮助

如果分数低于7分，请提供具体的修改建议。"""


CRITIC_USER_PROMPT = """评估以下研究报告：

公司：{company}
职位：{position}

报告：
{draft_report}

输出格式 - 只返回以下JSON结构，不要包含其他文字：
{{"score": 8, "summary": "简要评估总结", "suggestions": "如果分数<7则提供具体修改建议，否则为空字符串"}}
"""


async def critic_node(state: AgentState) -> dict[str, Any]:
    """Evaluate report quality and determine if revision is needed.

    Args:
        state: Current workflow state with draft_report

    Returns:
        Updated state with quality_score and revision_suggestions
    """
    if not state.draft_report:
        return {
            "quality_score": 0.0,
            "revision_suggestions": "没有可评估的报告",
            "messages": ["评论家: 没有可评估的报告"]
        }

    llm = create_llm(temperature=0.1)

    user_prompt = CRITIC_USER_PROMPT.format(
        company=state.target_company,
        position=state.target_position,
        draft_report=state.draft_report
    )

    try:
        response = await llm.ainvoke([
            SystemMessage(content=CRITIC_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])

        content = response.content.strip()

        # Log the thinking process
        log_think("critic", "evaluating", user_prompt, content, {
            "company": state.target_company,
            "position": state.target_position,
            "report_length": len(state.draft_report)
        })

        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        result = json.loads(content)

        score = float(result.get("score", 0))
        summary = result.get("summary", "")
        suggestions = result.get("suggestions", "")

        return {
            "quality_score": score,
            "revision_suggestions": suggestions,
            "messages": [f"评论家: 评分 {score}/10 - {summary}"]
        }

    except (json.JSONDecodeError, KeyError) as e:
        return {
            "errors": [f"评论家解析错误: {str(e)}"],
            "quality_score": 5.0,
            "revision_suggestions": "",
            "messages": [f"评论家: 解析响应出错，默认分数为5"]
        }
