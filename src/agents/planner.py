"""Planner Agent - generates research plan for job research."""
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import create_llm
from src.graph.state import AgentState, ResearchDimension
from src.think_log import log_think
import json


# System prompt for the Planner
PLANNER_SYSTEM_PROMPT = """你是一位求职研究规划专家。你的任务是根据目标公司和职位，创建一个结构化的研究计划。

对于给定的公司和职位，识别5-8个关键研究维度，帮助求职者有效准备面试。

每个研究维度应包含：
1. name: 研究领域的清晰简洁名称
2. search_keywords: 3-5个用于查找该信息的具体搜索关键词
3. priority: 基于面试准备重要性的"high"、"medium"或"low"

输出格式：返回JSON数组格式的研究维度。"""


PLANNER_USER_PROMPT = """分析以下职位信息，创建研究计划：

公司：{company}
职位：{position}

返回一个JSON数组格式的研究维度。例如：
[
  {{"name": "公司概况", "search_keywords": ["公司名称 历史", "创始故事", "使命价值观"], "priority": "high"}},
  {{"name": "技术栈", "search_keywords": ["公司 技术栈", "使用的编程语言", "技术基础设施"], "priority": "high"}}
]

只返回JSON数组，不要包含其他文字。"""


async def planner_node(state: AgentState) -> dict[str, Any]:
    """Generate research plan based on company and position.

    Args:
        state: Current workflow state with company and position

    Returns:
        Updated state with research_plan
    """
    if not state.target_company or not state.target_position:
        return {
            "errors": ["缺少目标公司或目标职位"],
            "research_plan": []
        }

    llm = create_llm(temperature=0.1)

    # Format prompt
    user_prompt = PLANNER_USER_PROMPT.format(
        company=state.target_company,
        position=state.target_position
    )

    # Invoke LLM
    response = await llm.ainvoke([
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])

    # Log the thinking process
    full_prompt = f"System: {PLANNER_SYSTEM_PROMPT}\n\nUser: {user_prompt}"
    log_think("planner", "planning", full_prompt, response.content, {
        "company": state.target_company,
        "position": state.target_position
    })

    # Parse response
    try:
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        plan_data = json.loads(content)

        # Convert to ResearchDimension objects
        research_plan = [
            ResearchDimension(
                name=item["name"],
                search_keywords=item["search_keywords"],
                priority=item.get("priority", "medium")
            )
            for item in plan_data
        ]

        return {
            "research_plan": research_plan,
            "messages": [f"规划师: 创建了包含 {len(research_plan)} 个维度的研究计划"]
        }

    except (json.JSONDecodeError, KeyError) as e:
        return {
            "errors": [f"解析规划师输出失败: {e}"],
            "research_plan": [],
            "messages": [f"规划师错误: {str(e)}"]
        }
