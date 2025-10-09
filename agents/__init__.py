"""
AI Agents Package
Contains all agent configurations and system prompts
"""

from . import (
    hr_assistant,
    financial_advisor,
    customer_support,
    tech_support,
    bank_advisor,
    travel_planner,
    code_reviewer,
    summarization_assistant,
    devops_automation,
    generic_chatbot,
    ecommerce_assistant,
    healthcare_scheduler
)

# Registry of all available agents
AVAILABLE_AGENTS = {
    "hr": hr_assistant,
    "financial": financial_advisor,
    "customer_support": customer_support,
    "tech_support": tech_support,
    "bank": bank_advisor,
    "travel": travel_planner,
    "code_review": code_reviewer,
    "summarization": summarization_assistant,
    "devops": devops_automation,
    "chatbot": generic_chatbot,
    "ecommerce": ecommerce_assistant,
    "healthcare": healthcare_scheduler
}

def get_agent(agent_key):
    """
    Get agent module by key

    Args:
        agent_key (str): Key of the agent to retrieve

    Returns:
        module: Agent module containing SYSTEM_PROMPT, AGENT_CONFIG, and TOOLS
    """
    if agent_key not in AVAILABLE_AGENTS:
        raise ValueError(f"Agent '{agent_key}' not found. Available agents: {list(AVAILABLE_AGENTS.keys())}")
    return AVAILABLE_AGENTS[agent_key]

def list_agents():
    """
    List all available agents with their descriptions

    Returns:
        dict: Dictionary of agent keys and their configurations
    """
    agents_info = {}
    for key, module in AVAILABLE_AGENTS.items():
        agents_info[key] = {
            "name": module.AGENT_CONFIG["name"],
            "description": module.AGENT_CONFIG["description"],
            "categories": module.AGENT_CONFIG["categories"],
            "has_tools": module.AGENT_CONFIG["has_tools"]
        }
    return agents_info
