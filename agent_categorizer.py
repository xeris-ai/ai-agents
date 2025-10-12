"""
Agent Categorization System using DSPy
Analyzes system prompts and categorizes agents with self-learning capabilities
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import dspy
from dspy import Signature, InputField, OutputField
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate

# Add the parent directory to path to import our agents
sys.path.insert(0, str(Path(__file__).parent))

from config.bedrock_config import invoke_bedrock_agent


@dataclass
class AgentCategory:
    """Represents an agent category with confidence score"""
    name: str
    confidence: float
    description: str = ""


@dataclass
class AgentAnalysis:
    """Complete analysis result for an agent"""
    type: str = "agent"
    categories: List[AgentCategory] = None
    has_tools: str = "no"
    confidence_threshold: float = 0.7
    reasoning: str = ""
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []


class AgentCategorizationSignature(Signature):
    """DSPy signature for agent categorization"""
    
    system_prompt = InputField(desc="The system prompt of the agent to categorize")
    existing_categories = InputField(desc="List of existing categories to choose from")
    
    analysis = OutputField(desc="JSON object categorizing the system prompt with: type (agent type), categories (list with confidence >90%), has_tools (boolean), and reasoning (explanation)")


class AgentCategorizer(dspy.Module):
    """DSPy module for categorizing agents"""
    
    def __init__(self):
        super().__init__()
        self.categorizer = dspy.ChainOfThought(AgentCategorizationSignature)
        
        # Initialize DSPy with Bedrock
        self._setup_dspy()
        
        # Load categories from file or use defaults
        self.categories_file = "categories.json"
        self.categories = self._load_categories()
    
    def _setup_dspy(self):
        """Setup DSPy with Bedrock configuration"""
        try:
            # Configure DSPy to use Bedrock via LM
            lm = dspy.LM(
                model="bedrock/anthropic.claude-3-5-haiku-20241022-v1:0",
                region_name="us-west-2",
                max_tokens=2000,
                temperature=0.7
            )
            dspy.configure(lm=lm)
            print("✅ DSPy configured with Bedrock")
        except Exception as e:
            print(f"❌ Failed to configure DSPy with Bedrock: {e}")
            # Fallback to OpenAI if available
            try:
                lm = dspy.LM(model="openai/gpt-3.5-turbo", max_tokens=2000)
                dspy.configure(lm=lm)
                print("✅ DSPy configured with OpenAI fallback")
            except Exception as e2:
                print(f"❌ Failed to configure DSPy: {e2}")
                # Use fallback categorization only
                print("⚠️ Using fallback categorization only")
    
    def _load_categories(self) -> List[str]:
        """Load categories from the categories.json file"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                categories = data.get('categories', [])
                print(f"✅ Loaded {len(categories)} categories from {self.categories_file}")
                return categories
        except FileNotFoundError:
            print(f"⚠️ Categories file {self.categories_file} not found, using defaults")
            return self._get_default_categories()
        except Exception as e:
            print(f"❌ Error loading categories: {e}, using defaults")
            return self._get_default_categories()
    
    def _get_default_categories(self) -> List[str]:
        """Get default categories list"""
        return [
            "customer support",
            "technical support", 
            "sales",
            "marketing",
            "finance",
            "healthcare",
            "education",
            "legal",
            "devops",
            "data analysis",
            "content creation",
            "assistant",
            "chatbot",
            "automation",
            "security",
            "research",
            "translation",
            "summarization",
            "code review",
            "travel planning"
        ]
    
    def _save_categories(self):
        """Save current categories to the categories.json file"""
        try:
            data = {
                "categories": self.categories,
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "Dynamic category list for agent categorization system"
                }
            }
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(self.categories)} categories to {self.categories_file}")
        except Exception as e:
            print(f"❌ Failed to save categories: {e}")
    
    def categorize_agent(self, system_prompt: str, existing_categories: Optional[List[str]] = None) -> AgentAnalysis:
        """
        Categorize an agent based on its system prompt
        
        Args:
            system_prompt: The system prompt to analyze
            existing_categories: Optional list of existing categories
            
        Returns:
            AgentAnalysis object with categorization results
        """
        if existing_categories is None:
            existing_categories = self.categories
        
        try:
            # Use DSPy to categorize
            result = self.categorizer(
                system_prompt=system_prompt,
                existing_categories=json.dumps(existing_categories)
            )
            
            # Parse the analysis result
            analysis_data = self._parse_analysis_result(result.analysis)
            
            return analysis_data
            
        except Exception as e:
            print(f"❌ Error in DSPy categorization: {e}")
            # Return empty analysis on error
            return AgentAnalysis(
                type="agent",
                categories=[],
                has_tools="unknown",
                reasoning=f"DSPy categorization failed: {e}"
            )
    
    def _parse_analysis_result(self, analysis_text: str) -> AgentAnalysis:
        """Parse the analysis result from DSPy"""
        try:
            # Try to extract JSON from the response
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_text = analysis_text[json_start:json_end].strip()
            elif "{" in analysis_text and "}" in analysis_text:
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                json_text = analysis_text[json_start:json_end]
            else:
                json_text = analysis_text
            
            data = json.loads(json_text)
            
            # Parse categories
            categories = []
            if "categories" in data:
                for cat in data["categories"]:
                    if isinstance(cat, dict):
                        name = cat.get("name", cat.get("category", ""))
                        confidence = cat.get("confidence", 1.0)
                    else:
                        name = str(cat)
                        confidence = 1.0
                    
                    if confidence >= 0.7:  # Only include high-confidence categories
                        categories.append(AgentCategory(
                            name=name,
                            confidence=confidence
                        ))
            
            return AgentAnalysis(
                type=data.get("type", "agent"),
                categories=categories,
                has_tools=data.get("has_tools", "no"),
                reasoning=data.get("reasoning", analysis_text)
            )
            
        except Exception as e:
            print(f"❌ Error parsing analysis result: {e}")
            # Return a basic analysis
            return AgentAnalysis(
                type="agent",
                categories=[AgentCategory(name="unknown", confidence=0.5)],
                has_tools="unknown",
                reasoning=f"Parse error: {e}"
            )
    
    
    def add_new_category(self, category_name: str, description: str = ""):
        """Add a new category to the categories list and save to file"""
        if category_name not in self.categories:
            self.categories.append(category_name)
            self._save_categories()  # Save to file immediately
            print(f"✅ Added new category: {category_name}")
        else:
            print(f"ℹ️ Category '{category_name}' already exists")
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories"""
        return self.categories.copy()


def analyze_agents_from_file(file_path: str) -> Dict[str, Any]:
    """Analyze agents from a file containing system prompts"""
    categorizer = AgentCategorizer()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON first
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "system_prompt" in data:
                return analyze_single_prompt(categorizer, data["system_prompt"])
            elif isinstance(data, list):
                return analyze_multiple_prompts(categorizer, data)
        except json.JSONDecodeError:
            pass
        
        # Treat as plain text system prompt
        return analyze_single_prompt(categorizer, content)
        
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}


def analyze_single_prompt(categorizer: AgentCategorizer, system_prompt: str) -> Dict[str, Any]:
    """Analyze a single system prompt"""
    print(f"🔍 Analyzing system prompt...")
    print(f"📝 Prompt length: {len(system_prompt)} characters")
    
    analysis = categorizer.categorize_agent(system_prompt)
    
    return {
        "input": {
            "system_prompt": system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt,
            "prompt_length": len(system_prompt)
        },
        "analysis": {
            "type": analysis.type,
            "categories": [
                {
                    "name": cat.name,
                    "confidence": round(cat.confidence, 2)
                }
                for cat in analysis.categories
            ],
            "has_tools": analysis.has_tools,
            "reasoning": analysis.reasoning
        },
        "available_categories": categorizer.get_available_categories()
    }


def analyze_multiple_prompts(categorizer: AgentCategorizer, prompts: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze multiple system prompts"""
    results = []
    
    for i, prompt_data in enumerate(prompts):
        if isinstance(prompt_data, dict) and "system_prompt" in prompt_data:
            system_prompt = prompt_data["system_prompt"]
            agent_name = prompt_data.get("name", f"Agent_{i+1}")
        else:
            system_prompt = str(prompt_data)
            agent_name = f"Agent_{i+1}"
        
        print(f"🔍 Analyzing {agent_name}...")
        analysis = categorizer.categorize_agent(system_prompt)
        
        results.append({
            "agent_name": agent_name,
            "analysis": {
                "type": analysis.type,
                "categories": [
                    {
                        "name": cat.name,
                        "confidence": round(cat.confidence, 2)
                    }
                    for cat in analysis.categories
                ],
                "has_tools": analysis.has_tools,
                "reasoning": analysis.reasoning
            }
        })
    
    return {
        "batch_analysis": results,
        "summary": {
            "total_agents": len(results),
            "available_categories": categorizer.get_available_categories()
        }
    }


def save_results(results: Dict[str, Any], output_file: str = None):
    """Save analysis results to file"""
    from datetime import datetime
    import os
    
    # Create results directory if it doesn't exist
    results_dir = "categorization_results"
    os.makedirs(results_dir, exist_ok=True)
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"agent_categorization_results_{timestamp}.json"
    
    # Ensure the output file is in the results directory
    if not os.path.dirname(output_file):
        output_file = os.path.join(results_dir, output_file)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")


def main():
    """Main function for the agent categorization application"""
    # Use default file path
    file_path = "all_agents.json"
    
    # Optional: allow custom file path as first argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    print(f"📁 Analyzing agents from file: {file_path}")
    results = analyze_agents_from_file(file_path)
    
    # Auto-generate output filename with timestamp and save to folder
    save_results(results)
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 ANALYSIS RESULTS")
    print("=" * 50)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
