#!/usr/bin/env python3
"""
AI Agent Runner
Main script to run different AI agents with AWS Bedrock
"""

import sys
import os
import logging
from config import invoke_bedrock_agent, BEDROCK_CONFIG
from agents import get_agent, list_agents, AVAILABLE_AGENTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def display_agents_menu():
    """Display numbered menu of all available agents"""
    agents_info = list_agents()
    agents_list = list(agents_info.items())

    logger.info("\n" + "="*70)
    logger.info("AVAILABLE AGENTS")
    logger.info("="*70 + "\n")

    for idx, (key, info) in enumerate(agents_list, 1):
        tools_indicator = "YES" if info["has_tools"] == "yes" else "NO"
        logger.info(f"[{idx}] {info['name']}")
        logger.info(f"    Key: {key}")
        logger.info(f"    Description: {info['description']}")
        logger.info(f"    Tools: {tools_indicator}")
        logger.info("")

    logger.info("="*70)
    return agents_list


def chat_with_agent(agent_key):
    """Interactive chat session with selected agent"""
    agent_module = get_agent(agent_key)

    logger.info("\n" + "="*70)
    logger.info(f"CHATTING WITH: {agent_module.AGENT_CONFIG['name']}")
    logger.info("="*70)
    logger.info(f"\nDescription: {agent_module.AGENT_CONFIG['description']}")
    logger.info(f"Categories: {', '.join(agent_module.AGENT_CONFIG['categories'])}")
    logger.info(f"Tools Available: {len(agent_module.TOOLS)}")
    if agent_module.TOOLS:
        logger.info(f"Tools: {', '.join(agent_module.TOOLS[:3])}{'...' if len(agent_module.TOOLS) > 3 else ''}")

    logger.info("\n" + "-"*70)
    logger.info("Configuration:")
    logger.info(f"  Region: {BEDROCK_CONFIG['region']}")
    logger.info(f"  Model: {BEDROCK_CONFIG['model_id']}")
    logger.info(f"  Max Tokens: {BEDROCK_CONFIG['max_tokens']}")
    logger.info("-"*70)

    logger.info("\nType your message (or 'quit' to exit, 'back' to choose another agent)")
    logger.info("="*70 + "\n")

    while True:
        try:
            user_message = input("You: ").strip()

            if not user_message:
                continue

            logger.info(f"\n{agent_module.AGENT_CONFIG['name']}: ")

            try:
                response = invoke_bedrock_agent(
                    agent_system_prompt=agent_module.SYSTEM_PROMPT,
                    user_message=user_message,
                    tools=agent_module.TOOLS
                )
                logger.info(response)

            except Exception as e:
                logger.error(f"Error calling Bedrock: {e}")
                logger.error(f"Error calling Bedrock: {e}")
            logger.info("")  # Empty line for readability

        except KeyboardInterrupt:
            logger.info("\n\nSession interrupted. Returning to menu...\n")
            return True
        except EOFError:
            logger.info("\n\nGoodbye!\n")
            return False


def main():
    """Main interactive loop"""

    logger.info("\n" + "="*70)
    logger.info("AI AGENT CHAT - AWS Bedrock")
    logger.info("="*70)

    while True:
        # Display menu
        agents_list = display_agents_menu()

        # Get user selection
        try:
            choice = input("Select agent number (or 'q' to quit): ").strip()

            if choice.lower() in ['q', 'quit', 'exit']:
                logger.info("\nGoodbye!\n")
                break

            # Validate selection
            try:
                agent_num = int(choice)
                if 1 <= agent_num <= len(agents_list):
                    agent_key = agents_list[agent_num - 1][0]
                    # Start chat with selected agent
                    chat_with_agent(agent_key)
                else:
                    logger.warning(f"\nInvalid selection. Please choose 1-{len(agents_list)}\n")
            except ValueError:
                logger.warning("\nPlease enter a valid number\n")

        except KeyboardInterrupt:
            logger.info("\n\nGoodbye!\n")
            break
        except EOFError:
            logger.info("\n\nGoodbye!\n")
            break


if __name__ == "__main__":
    main()
