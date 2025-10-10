#!/usr/bin/env python3
"""
AI Agent Runner
Main script to run different AI agents with AWS Bedrock
"""

import sys
import os
from config import invoke_bedrock_agent, BEDROCK_CONFIG
from agents import get_agent, list_agents, AVAILABLE_AGENTS


def display_agents_menu():
    """Display numbered menu of all available agents"""
    agents_info = list_agents()
    agents_list = list(agents_info.items())

    print("\n" + "="*70)
    print("AVAILABLE AGENTS")
    print("="*70 + "\n")

    for idx, (key, info) in enumerate(agents_list, 1):
        tools_indicator = "✓" if info["has_tools"] == "yes" else "✗"
        print(f"[{idx}] {info['name']}")
        print(f"    Key: {key}")
        print(f"    Description: {info['description']}")
        print(f"    Tools: {tools_indicator}")
        print()

    print("="*70)
    return agents_list


def chat_with_agent(agent_key):
    """Interactive chat session with selected agent"""
    agent_module = get_agent(agent_key)

    print("\n" + "="*70)
    print(f"CHATTING WITH: {agent_module.AGENT_CONFIG['name']}")
    print("="*70)
    print(f"\nDescription: {agent_module.AGENT_CONFIG['description']}")
    print(f"Categories: {', '.join(agent_module.AGENT_CONFIG['categories'])}")
    print(f"Tools Available: {len(agent_module.TOOLS)}")
    if agent_module.TOOLS:
        print(f"Tools: {', '.join(agent_module.TOOLS[:3])}{'...' if len(agent_module.TOOLS) > 3 else ''}")

    print("\n" + "-"*70)
    print("Configuration:")
    print(f"  Region: {BEDROCK_CONFIG['region']}")
    print(f"  Model: {BEDROCK_CONFIG['model_id']}")
    print(f"  Max Tokens: {BEDROCK_CONFIG['max_tokens']}")
    print("-"*70)

    print("\nType your message (or 'quit' to exit, 'back' to choose another agent)")
    print("="*70 + "\n")

    while True:
        try:
            user_message = input("You: ").strip()

            if not user_message:
                continue

            print(f"\n{agent_module.AGENT_CONFIG['name']}: ", end="", flush=True)

            try:
                response = invoke_bedrock_agent(
                    agent_system_prompt=agent_module.SYSTEM_PROMPT,
                    user_message=user_message,
                    tools=agent_module.TOOLS
                )
                print(response)

            except Exception as e:
                print(f"\n✗ Error calling Bedrock: {e}")
            print()  # Empty line for readability

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Returning to menu...\n")
            return True
        except EOFError:
            print("\n\nGoodbye! 👋\n")
            return False


def main():
    """Main interactive loop"""

    print("\n" + "="*70)
    print("AI AGENT CHAT - AWS Bedrock")
    print("="*70)

    while True:
        # Display menu
        agents_list = display_agents_menu()

        # Get user selection
        try:
            choice = input("Select agent number (or 'q' to quit): ").strip()

            if choice.lower() in ['q', 'quit', 'exit']:
                print("\nGoodbye! 👋\n")
                break

            # Validate selection
            try:
                agent_num = int(choice)
                if 1 <= agent_num <= len(agents_list):
                    agent_key = agents_list[agent_num - 1][0]
                    # Start chat with selected agent
                    chat_with_agent(agent_key)
                else:
                    print(f"\n✗ Invalid selection. Please choose 1-{len(agents_list)}\n")
            except ValueError:
                print("\n✗ Please enter a valid number\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except EOFError:
            print("\n\nGoodbye! 👋\n")
            break


if __name__ == "__main__":
    main()
