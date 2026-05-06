"""Researcher Agent - searches for information on research dimensions."""
import asyncio
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from duckduckgo_search import DDGS
from src.llm import create_llm
from src.config import settings
from src.graph.state import AgentState, ResearchDimension
from src.think_log import log_think


RESEARCHER_SYSTEM_PROMPT = """你是一位研究助手。根据给定研究维度的搜索结果，用简洁的段落总结关键发现。

重点关注有助于求职者准备面试的事实信息。
尽可能包含具体的数字、技术和流程细节。"""


async def search_dimension(
    dimension: ResearchDimension,
    company: str,
    position: str,
    max_results: int = 5
) -> tuple[str, str]:
    """Search for information on a single research dimension.

    Args:
        dimension: The research dimension to search
        company: Target company name
        position: Target position name
        max_results: Maximum number of search results

    Returns:
        Tuple of (dimension_name, findings_summary)
    """
    search_queries = [
        f"{company} {position} {keyword}"
        for keyword in dimension.search_keywords[:2]
    ]

    all_results = []

    with DDGS() as ddgs:
        for query in search_queries:
            try:
                results = list(ddgs.text(query, max_results=max_results))
                for r in results:
                    all_results.append({
                        "title": r.get("title", ""),
                        "href": r.get("href", ""),
                        "body": r.get("body", "")
                    })
            except Exception:
                continue

    if not all_results:
        return dimension.name, f"未找到关于 {dimension.name} 的搜索结果"

    # Format results for summarization
    results_text = "\n\n".join([
        f"来源: {r['title']}\n链接: {r['href']}\n内容: {r['body'][:500]}"
        for r in all_results[:3]
    ])

    # Use LLM to summarize
    llm = create_llm(temperature=0.1)

    summary_prompt = f"""根据以下关于"{dimension.name}"的搜索结果，总结关键发现：

{results_text}

提供2-3句简洁的总结，包含与求职准备相关的具体事实细节。"""

    try:
        response = await llm.ainvoke([
            SystemMessage(content=RESEARCHER_SYSTEM_PROMPT),
            HumanMessage(content=summary_prompt)
        ])
        findings = response.content.strip()

        # Log the thinking process
        log_think("researcher", f"summarize_{dimension.name}", summary_prompt, findings, {
            "company": company,
            "position": position,
            "dimension": dimension.name,
            "search_results_count": len(all_results)
        })
    except Exception as e:
        findings = f"总结结果时出错: {str(e)}"

    return dimension.name, findings


async def researcher_node(state: AgentState) -> dict[str, Any]:
    """Search all research dimensions in parallel.

    Args:
        state: Current workflow state with research_plan

    Returns:
        Updated state with research_results
    """
    if not state.research_plan:
        return {
            "errors": ["没有可用的研究计划"],
            "research_results": {}
        }

    company = state.target_company
    position = state.target_position

    # Execute searches in parallel
    tasks = [
        search_dimension(dimension, company, position, settings.max_search_results)
        for dimension in state.research_plan
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    research_results = {}
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(f"搜索错误: {str(result)}")
        else:
            dimension_name, findings = result
            research_results[dimension_name] = findings

    return {
        "research_results": research_results,
        "errors": errors if errors else None,
        "messages": [f"研究员: 完成了 {len(research_results)}/{len(state.research_plan)} 个维度的研究"]
    }
