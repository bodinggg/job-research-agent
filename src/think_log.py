"""Think log utility for logging LLM prompts and responses."""
import json
import os
from datetime import datetime
from pathlib import Path


def get_think_log_dir() -> Path:
    """Get or create the think log directory."""
    log_dir = Path("think_log")
    log_dir.mkdir(exist_ok=True)
    return log_dir


def log_think(agent_name: str, stage: str, prompt: str, response: str, metadata: dict = None) -> str:
    """Log an agent's thinking process to a file.

    Args:
        agent_name: Name of the agent (planner, researcher, writer, critic)
        stage: Current stage (e.g., "planning", "summarizing", "writing")
        prompt: The prompt sent to LLM
        response: The response from LLM
        metadata: Additional metadata to log

    Returns:
        Path to the log file created
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{agent_name}_{stage}_{timestamp}.json"
    filepath = get_think_log_dir() / filename

    log_entry = {
        "agent": agent_name,
        "stage": stage,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "metadata": metadata or {}
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)

    return str(filepath)
