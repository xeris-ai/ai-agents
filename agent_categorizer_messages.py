#!/usr/bin/env python3
"""
Agent Message Categorization System using DSPy
Analyzes conversation messages and categorizes them with self-learning capabilities
"""
import json
from typing import List, Dict
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
    "troubleshooting", "news", "search", "information retrieval", "web search"
]

# 1) Structured schema you want back
class MessageAnalysis(BaseModel):
    categories: List[str] = Field(..., description="High-confidence categories (>80%)")
    category_statistics: Dict[str, float] = Field(..., description="Dictionary mapping ALL provided categories to their percentage of messages (0.0 to 100.0).")
    reasoning: str = Field(..., description="Explanation of the categorization")

# 2) Define a "schema tool": the LM will call this with JSON args we want.
#    Body won't actually run; we just harvest the call args.
def _emit_message_analysis(
    categories: List[str],
    category_statistics: Dict[str, float],
    reasoning: str,
) -> str:
    """Emit a MessageAnalysis (used purely for function-calling argument collection)."""
    return "ok"

schema_tool = dspy.Tool(
    _emit_message_analysis,
    name="categorize_messages",
    desc="Categorize EACH INDIVIDUAL MESSAGE. CRITICAL: categories must ONLY be selected from the provided existing_categories list. Count each message separately. MANDATORY FIELDS: categories (list of strings from existing_categories), category_statistics (REQUIRED: dict mapping ALL provided categories to their percentage 0.0-100.0 based on individual message counts, unused categories show 0.0), reasoning (string). You MUST provide category_statistics with ALL categories from existing_categories."
)

# 3) Signature that asks the LM to produce TOOL CALLS (not free text)
class MessageCategorizationSignature(dspy.Signature):
    messages: str = dspy.InputField(desc="Conversation messages to analyze.")
    existing_categories: List[str] = dspy.InputField(desc="STRICT: Only choose categories from this exact list. If no match, use 'other'. You MUST provide category_statistics for ALL these categories.")
    tools: List[dspy.Tool] = dspy.InputField(desc="Available tools for categorization.")
    # The model returns a list of tool calls; we'll read the first one.
    outputs: dspy.ToolCalls = dspy.OutputField()

# 4) Module that executes prediction, then validates tool-call args as JSON
class MessageCategorizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # Simple single-step predictor
        self.predict = dspy.Predict(MessageCategorizationSignature)

    def _format_messages_for_analysis(self, messages: List[dict]) -> str:
        """Format messages into a readable string for analysis."""
        formatted_messages = []
        
        for i, message in enumerate(messages, 1):
            role = message.get("role", "unknown")
            content = message.get("content", [])
            
            # Extract text content
            text_content = ""
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        text_content += item["text"] + " "
            elif isinstance(content, str):
                text_content = content
            
            # Format with clear message numbering and separation
            formatted_messages.append(f"MESSAGE {i} - {role.upper()}: {text_content.strip()}")
        
        return "\n\n".join(formatted_messages)

    def forward(self, messages: List[dict], existing_categories: List[str]) -> List[MessageAnalysis]:
        results: List[MessageAnalysis] = []
        
        # Format messages for analysis
        formatted_messages = self._format_messages_for_analysis(messages)
        
        # Debug logging
        logger.info(f"Processing {len(messages)} messages for categorization")
        logger.info(f"Formatted messages preview: {formatted_messages[:200]}...")
        
        # Add 'other' category to the list of available categories
        categories_with_other = existing_categories + ["other"]
        
        try:
            pred = self.predict(
                messages=formatted_messages,
                existing_categories=categories_with_other,
                tools=[schema_tool], 
            )
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return results


        # Expect at least one tool call
        calls = getattr(pred.outputs, "tool_calls", None)
        if not calls:
            raise RuntimeError("Model returned no tool calls; cannot extract JSON.")

        call = calls[0]
        if call.name != "categorize_messages":
            raise RuntimeError(f"Unexpected tool called: {call.name}")

        # These are the JSON args from the model
        args = call.args  # <-- dict
        
      
        
        try:
            results.append(MessageAnalysis(**args))  # Pydantic validation
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {e}") from e

        return results


def main():
    parser = argparse.ArgumentParser(description="Message Categorization with Native Function Calling")
   
    parser.add_argument(
        "--categories",
        nargs="*",
        default=DEFAULT_CATEGORIES,
        help="List of categories to use for classification (defaults to built-in list)."
    )
    parser.add_argument(
        "--messages",
        help="JSON string of messages list, where each message has 'role' and 'content' fields"
    )
    
    
    args = parser.parse_args()
    
    # Configure DSPy to use native function calling with specified temperature
    dspy.configure(
        lm=dspy.LM(
            model="bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"
        ),
        adapter=dspy.ChatAdapter(use_native_function_calling=True),
    )
    
    if not args.messages:
        logger.error("Please provide --messages")
        return
    
    # Load messages

    try:
        messages = json.loads(args.messages)
        # Validate that messages is a list of objects with role and content
        if not isinstance(messages, list):
            logger.error("Messages must be a list of message objects")
            return
        
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                logger.error(f"Message {i} must be an object")
                return
            if 'role' not in msg or 'content' not in msg:
                logger.error(f"Message {i} must have 'role' and 'content' fields")
                return
        
        logger.info(f"Loaded {len(messages)} messages from JSON string")
    except Exception as e:
        logger.error(f"Failed to parse messages JSON: {e}")
        return

    
    categories: List[str] = args.categories
    categorizer = MessageCategorizer()

    logger.info(f"Categorizing {len(messages)} message(s) using {len(categories)} categories...")
    logger.info("Using native function calling for guaranteed JSON output")
    
    try:
        output = categorizer.forward(
            messages=messages,
            existing_categories=categories
        )
        
        # Pretty print the JSON output
        for i, result in enumerate(output):
            logger.info(f"\n=== Message Analysis {i+1} ===")
            logger.info(result.model_dump_json(indent=2))
            
    except Exception as e:
        logger.error(f"Error during categorization: {e}")


if __name__ == "__main__":
    main()
