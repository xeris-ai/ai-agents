"""
Agent Categorization System using DSPy
Analyzes system prompts and categorizes agents with self-learning capabilities
"""

from typing import List
import dspy
from pydantic import BaseModel, Field, ValidationError
import logging
import argparse
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DEFAULT_CATEGORIES = [
    "customer support", "technical support", "sales", "marketing", "finance",
    "healthcare", "education", "legal", "devops", "data analysis",
    "content creation", "assistant", "chatbot", "automation", "security",
    "research", "translation", "summarization", "code review", "travel planning",
    "DevOps", "HR", "IT support", "appointment scheduling", "bank advisor",
    "banking", "content processing", "conversational AI", "e-commerce",
    "employee assistant", "financial advisor", "financial services",
    "general chatbot", "human resources", "infrastructure", "investment",
    "medical assistant", "quality assurance", "retail", "shopping assistant",
    "software development", "tourism", "travel planner", "trip planning",
    "troubleshooting"
]



# 1) Structured schema 
class AgentAnalysis(BaseModel):
    type: str
    categories: List[str] = Field(..., description="High-confidence categories (>90%)")
    has_tools: bool
    reasoning: str

# 2) Define a "schema tool": the LM will call this with JSON args we want.
#    Body won't actually run; we just harvest the call args.
def _emit_agent_analysis(
    type: str,
    categories: List[str],
    has_tools: bool,
    reasoning: str,
) -> str:
    """Emit an AgentAnalysis (used purely for function-calling argument collection)."""
    return "ok"

schema_tool = dspy.Tool(
    _emit_agent_analysis,
    name="categorize_agent",
    desc="Return fields: type, categories, has_tools, reasoning (as an AgentAnalysis)."
)

# 3) Signature that asks the LM to produce TOOL CALLS (not free text)
class AgentCategorizationSignature(dspy.Signature):
    system_prompt: str = dspy.InputField(desc="System prompt to analyze.")
    existing_categories: List[str] = dspy.InputField(desc="Known category labels.")
    tools: List[dspy.Tool] = dspy.InputField(desc="Available tools for categorization.")
    # The model returns a list of tool calls; we'll read the first one.
    outputs: dspy.ToolCalls = dspy.OutputField()

# 4) Module that executes prediction, then validates tool-call args as JSON
class AgentCategorizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # Simple single-step predictor
        self.predict = dspy.Predict(AgentCategorizationSignature)

    def forward(self, system_prompt: List[str], existing_categories: List[str]) -> List[AgentAnalysis]:
        results: List[AgentAnalysis] = []
        for prompt in system_prompt:
            pred = self.predict(
                system_prompt=prompt,
                existing_categories=existing_categories,
                tools=[schema_tool],  # Supply exactly one tool: we WANT the LM to call this.
            )

            # Expect at least one tool call
            calls = getattr(pred.outputs, "tool_calls", None)
            if not calls:
                raise RuntimeError("Model returned no tool calls; cannot extract JSON.")

            call = calls[0]
            if call.name != "categorize_agent":
                raise RuntimeError(f"Unexpected tool called: {call.name}")

            # These are the JSON args from the model
            args = call.args  # <-- dict
            try:
                results.append(AgentAnalysis(**args))  # Pydantic validation
            except ValidationError as e:
                raise ValueError(f"Schema validation failed: {e}") from e

        return results


def main():
    # Configure DSPy to use native function calling (recommended)
    dspy.configure(
        lm=dspy.LM(model="bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"),
        adapter=dspy.ChatAdapter(use_native_function_calling=True),
    )
    
    parser = argparse.ArgumentParser(description="Agent Categorization with Native Function Calling")
    parser.add_argument(
        "--prompt",
        action="append",
        help="A system prompt to categorize. Use multiple --prompt flags for multiple prompts."
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        default=DEFAULT_CATEGORIES,
        help="List of categories to use for classification (defaults to built-in list)."
    )
    args = parser.parse_args()
    prompts: List[str] = []
    categories: List[str] = args.categories
    if args.prompt:
        prompts.extend(args.prompt)
    agent = AgentCategorizer()

    logger.info(f"Categorizing {len(prompts)} prompt(s) using {len(categories)} categories...")
    
    output = agent.forward(
        system_prompt=prompts,
        existing_categories=categories
    )
    
    # Pretty print the JSON output
    for i, result in enumerate(output):
        logger.info(f"\n=== Analysis {i+1} ===")
        logger.info(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()