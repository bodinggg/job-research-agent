"""LangGraph workflow orchestration."""
from typing import Literal
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.agents import planner, researcher, writer, critic


# Quality threshold for accepting report
QUALITY_THRESHOLD = 7.0


def should_rewrite(state: AgentState) -> Literal["writer", "finalize"]:
    """Determine if the report needs rewriting based on quality score.

    Args:
        state: Current workflow state

    Returns:
        "writer" to trigger rewrite, "finalize" to accept report
    """
    # Check if we've exceeded max rewrites
    if state.rewrite_count >= state.max_rewrites:
        return "finalize"

    # Check quality score
    if state.quality_score < QUALITY_THRESHOLD:
        return "writer"

    return "finalize"


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow for job research.

    Returns:
        Compiled StateGraph for the research workflow
    """
    # Define the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner.planner_node)
    workflow.add_node("researcher", researcher.researcher_node)
    workflow.add_node("writer", writer.writer_node)
    workflow.add_node("critic", critic.critic_node)

    # Define edges - linear flow
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "critic")

    # Add conditional edge from critic
    workflow.add_conditional_edges(
        "critic",
        should_rewrite,
        {
            "writer": "writer",  # Rewrite loop
            "finalize": END
        }
    )

    # Compile the graph
    return workflow.compile()


# Global workflow instance
_workflow = None


def get_workflow() -> StateGraph:
    """Get or create the workflow singleton.

    Returns:
        Compiled StateGraph instance
    """
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow


async def run_research(company: str, position: str) -> AgentState:
    """Run the complete research workflow.

    Args:
        company: Target company name
        position: Target position name

    Returns:
        Final AgentState with research results
    """
    workflow = get_workflow()

    initial_state = AgentState(
        user_input=f"{company} {position}",
        target_company=company,
        target_position=position
    )

    # Run the workflow
    final_state = await workflow.ainvoke(initial_state)

    # LangGraph returns dict, handle both dict and object access
    final_state_dict = dict(final_state) if hasattr(final_state, '__iter__') else final_state
    quality_score = final_state_dict.get('quality_score', 0)
    rewrite_count = final_state_dict.get('rewrite_count', 0)

    # If report is accepted, set final_report
    if quality_score >= QUALITY_THRESHOLD or rewrite_count >= initial_state.max_rewrites:
        final_state_dict['final_report'] = final_state_dict.get('draft_report', '')

    return final_state_dict
