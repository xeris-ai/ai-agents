#!/usr/bin/env python3
"""
Extract all system prompts from agents folder into a JSON file
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to path to import our agents
sys.path.insert(0, str(Path(__file__).parent))

from agents import list_agents, get_agent


def extract_all_agents_to_file(output_file: str = None):
    """Extract all agents' system prompts to a JSON file"""
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"all_agents_system_prompts_{timestamp}.json"
    
    agents_data = []
    
    try:
        agents_info = list_agents()
        
        for agent_key, agent_info in agents_info.items():
            try:
                agent_module = get_agent(agent_key)
                
                agent_data = {
                    "agent_key": agent_key,
                    "name": agent_module.AGENT_CONFIG.get("name", agent_key),
                    "description": agent_module.AGENT_CONFIG.get("description", ""),
                    "categories": agent_module.AGENT_CONFIG.get("categories", []),
                    "system_prompt": agent_module.SYSTEM_PROMPT,
                    "has_tools": len(agent_module.TOOLS) > 0 if hasattr(agent_module, 'TOOLS') else False,
                    "tools_count": len(agent_module.TOOLS) if hasattr(agent_module, 'TOOLS') else 0
                }
                
                agents_data.append(agent_data)
                print(f"✅ Extracted: {agent_data['name']}")
                
            except Exception as e:
                print(f"❌ Failed to extract {agent_key}: {e}")
                continue
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(agents_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Extracted {len(agents_data)} agents to: {output_file}")
        print(f"📊 Total system prompts: {len(agents_data)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Failed to extract agents: {e}")
        return None


def main():
    """Main function"""
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = None
    
    print("🚀 Extracting all agent system prompts...")
    print("=" * 50)
    
    result_file = extract_all_agents_to_file(output_file)
    
    if result_file:
        print(f"\n🎉 Success! Use this file with agent_categorizer.py:")
        print(f"python agent_categorizer.py {result_file}")


if __name__ == "__main__":
    main()
