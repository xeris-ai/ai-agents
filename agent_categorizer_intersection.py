#!/usr/bin/env python3
"""
Agent Categorization Intersection System
Creates instances of message and prompt agents, runs them, and calculates category intersections
"""

from typing import List, Dict, Set, Tuple
import dspy
from pydantic import BaseModel, Field
import logging
import argparse
import json
from datetime import datetime

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

# Import the existing agents
from agent_categorizer_messages import MessageCategorizer, MessageAnalysis
from agent_categorizer_prompts import AgentCategorizer, AgentAnalysis

class IntersectionResult(BaseModel):
    """Result of intersecting message and prompt categorizations"""
    messages_categories: List[str] = Field(..., description="Categories from message analysis")
    prompt_categories: List[str] = Field(..., description="Categories from prompt analysis")
    intersection_categories: List[str] = Field(..., description="Categories found in both analyses")
    messages_only_categories: List[str] = Field(..., description="Categories only in messages")
    prompt_only_categories: List[str] = Field(..., description="Categories only in prompt")
    messages_analysis: MessageAnalysis = Field(..., description="Full message analysis result")
    prompt_analysis: AgentAnalysis = Field(..., description="Full prompt analysis result")
    intersection_score: float = Field(..., description="Intersection score (0-1)")
    union_size: int = Field(..., description="Total unique categories")
    intersection_size: int = Field(..., description="Number of intersecting categories")

class ComprehensiveOutput(BaseModel):
    """Comprehensive output containing all analysis data"""
    timestamp: str = Field(..., description="Analysis timestamp")
    messages: List[Dict] = Field(..., description="Input messages")
    system_prompt: str = Field(..., description="System prompt analyzed")
    existing_categories: List[str] = Field(..., description="Available categories for classification")
    messages_categorization: MessageAnalysis = Field(..., description="Message categorization result")
    prompt_categorization: AgentAnalysis = Field(..., description="Prompt categorization result")
    intersection_result: IntersectionResult = Field(..., description="Intersection analysis result")
    analysis_summary: Dict = Field(..., description="Summary statistics")

class AgentCategorizationIntersection:
    """Manages intersection between message and prompt categorizations"""
    
    def __init__(self):
        self.message_agent = MessageCategorizer()
        self.prompt_agent = AgentCategorizer()  # Using proper prompt agent
    
    def _calculate_intersection_score(self, categories1: List[str], categories2: List[str]) -> Tuple[float, int, int]:
        """Calculate intersection score and statistics"""
        set1 = set(categories1)
        set2 = set(categories2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        intersection_size = len(intersection)
        union_size = len(union)
        
        # Intersection score: ratio of intersection to union
        intersection_score = intersection_size / union_size if union_size > 0 else 0.0
        
        return intersection_score, union_size, intersection_size
    
    def calculate_intersection(
        self, 
        messages: List[Dict], 
        system_prompt: str, 
        existing_categories: List[str]
    ) -> IntersectionResult:
        """
        Calculate intersection between message and prompt categorizations
        
        Args:
            messages: List of message objects with 'role' and 'content' fields
            system_prompt: System prompt string
            existing_categories: List of available categories
            
        Returns:
            IntersectionResult with detailed intersection analysis
        """
        logger.info("Starting categorization intersection calculation...")
        
        # Analyze messages using message agent
        logger.info("Analyzing messages with message agent...")
        messages_results = self.message_agent.forward(
            messages=messages,
            existing_categories=existing_categories
        )
        messages_analysis = messages_results[0] if messages_results else None
        
        if not messages_analysis:
            raise ValueError("Failed to analyze messages")
        
        # Analyze system prompt using prompt agent
        logger.info("Analyzing system prompt with prompt agent...")
        prompt_results = self.prompt_agent.forward(
            system_prompt=[system_prompt],
            existing_categories=existing_categories
        )
        prompt_analysis = prompt_results[0] if prompt_results else None
        
        if not prompt_analysis:
            raise ValueError("Failed to analyze system prompt")
        
        # Extract categories
        messages_categories = messages_analysis.categories
        prompt_categories = prompt_analysis.categories
        
        # Calculate intersections
        messages_set = set(messages_categories)
        prompt_set = set(prompt_categories)
        
        intersection_categories = list(messages_set.intersection(prompt_set))
        messages_only_categories = list(messages_set - prompt_set)
        prompt_only_categories = list(prompt_set - messages_set)
        
        # Calculate intersection score and statistics
        intersection_score, union_size, intersection_size = self._calculate_intersection_score(
            messages_categories, prompt_categories
        )
        
        logger.info(f"Intersection calculation complete. Score: {intersection_score:.2f}")
        logger.info(f"Intersection: {intersection_size} categories, Union: {union_size} categories")
        
        return IntersectionResult(
            messages_categories=messages_categories,
            prompt_categories=prompt_categories,
            intersection_categories=intersection_categories,
            messages_only_categories=messages_only_categories,
            prompt_only_categories=prompt_only_categories,
            messages_analysis=messages_analysis,
            prompt_analysis=prompt_analysis,
            intersection_score=intersection_score,
            union_size=union_size,
            intersection_size=intersection_size
        )
    
    def create_comprehensive_output(
        self,
        messages: List[Dict],
        system_prompt: str,
        existing_categories: List[str],
        intersection_result: IntersectionResult
    ) -> ComprehensiveOutput:
        """Create comprehensive output with all analysis data"""
        timestamp = datetime.now().isoformat()
        
        # Create analysis summary
        analysis_summary = {
            "total_messages": len(messages),
            "total_categories_available": len(existing_categories),
            "messages_categories_count": len(intersection_result.messages_categories),
            "prompt_categories_count": len(intersection_result.prompt_categories),
            "intersection_categories_count": len(intersection_result.intersection_categories),
            "messages_only_count": len(intersection_result.messages_only_categories),
            "prompt_only_count": len(intersection_result.prompt_only_categories),
            "intersection_score": intersection_result.intersection_score,
            "union_size": intersection_result.union_size,
            "intersection_size": intersection_result.intersection_size
        }
        
        return ComprehensiveOutput(
            timestamp=timestamp,
            messages=messages,
            system_prompt=system_prompt,
            existing_categories=existing_categories,
            messages_categorization=intersection_result.messages_analysis,
            prompt_categorization=intersection_result.prompt_analysis,
            intersection_result=intersection_result,
            analysis_summary=analysis_summary
        )

def main():
    # Configure DSPy
    dspy.configure(
        lm=dspy.LM(model="bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"),
        adapter=dspy.ChatAdapter(use_native_function_calling=True),
    )
    
    parser = argparse.ArgumentParser(description="Calculate intersection between message and prompt categorizations")
    parser.add_argument(
        "--messages",
        required=False,
        help="JSON string of messages list, where each message has 'role' and 'content' fields"
    )
    parser.add_argument(
        "--messages-file",
        help="JSON file containing messages list, where each message has 'role' and 'content' fields"
    )
    parser.add_argument(
        "--system-prompt",
        required=True,
        help="System prompt string to analyze"
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        default=DEFAULT_CATEGORIES,
        help="List of categories to use for classification (defaults to built-in list)."
    )
    parser.add_argument(
        "--output-file",
        help="File to save comprehensive analysis results as JSON"
    )

    
    args = parser.parse_args()
    
    # Validate that either messages or messages-file is provided
    if not args.messages and not args.messages_file:
        logger.error("Either --messages or --messages-file must be provided")
        return
    
    if args.messages and args.messages_file:
        logger.error("Cannot provide both --messages and --messages-file")
        return
    
    # Parse messages
    try:
        if args.messages_file:
            # Load messages from file
            with open(args.messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different file formats
            if isinstance(data, dict) and 'messages' in data:
                messages = data['messages']
            elif isinstance(data, list):
                messages = data
            else:
                logger.error("Invalid file format. Expected JSON with 'messages' key or array of messages")
                return
        else:
            # Parse messages from command line
            messages = json.loads(args.messages)
        
        # Validate messages format
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
        
        logger.info(f"Loaded {len(messages)} messages for analysis")
        
    except Exception as e:
        logger.error(f"Failed to parse messages: {e}")
        return
    
    # Initialize intersection calculator
    intersection_calculator = AgentCategorizationIntersection()
    
    try:
        # Calculate intersection
        result = intersection_calculator.calculate_intersection(
            messages=messages,
            system_prompt=args.system_prompt,
            existing_categories=args.categories
        )
        
        # Create comprehensive output
        comprehensive_output = intersection_calculator.create_comprehensive_output(
            messages=messages,
            system_prompt=args.system_prompt,
            existing_categories=args.categories,
            intersection_result=result
        )
        
        # Display results
        logger.info("\n" + "="*70)
        logger.info("CATEGORIZATION INTERSECTION RESULTS")
        logger.info("="*70)
        
        logger.info(f"\nINTERSECTION STATISTICS:")
        logger.info(f"  • Intersection Score: {result.intersection_score:.2f}")
        logger.info(f"  • Intersection Size: {result.intersection_size} categories")
        logger.info(f"  • Union Size: {result.union_size} categories")
        logger.info(f"  • Messages Categories: {len(result.messages_categories)}")
        logger.info(f"  • Prompt Categories: {len(result.prompt_categories)}")
        
        logger.info(f"\nMESSAGES CATEGORIES ({len(result.messages_categories)}):")
        for category in result.messages_categories:
            logger.info(f"  • {category}")
        
        logger.info(f"\nPROMPT CATEGORIES ({len(result.prompt_categories)}):")
        for category in result.prompt_categories:
            logger.info(f"  • {category}")
        
        logger.info(f"\nINTERSECTION CATEGORIES ({len(result.intersection_categories)}):")
        for category in result.intersection_categories:
            logger.info(f"  • {category}")
        
        logger.info(f"\nMESSAGES ONLY ({len(result.messages_only_categories)}):")
        for category in result.messages_only_categories:
            logger.info(f"  • {category}")
        
        logger.info(f"\nPROMPT ONLY ({len(result.prompt_only_categories)}):")
        for category in result.prompt_only_categories:
            logger.info(f"  • {category}")
        
        # Display detailed analysis
        logger.info(f"\nDETAILED MESSAGES ANALYSIS:")
        logger.info(result.messages_analysis.model_dump_json(indent=2))
        
        logger.info(f"\nDETAILED PROMPT ANALYSIS:")
        logger.info(result.prompt_analysis.model_dump_json(indent=2))
        
        # Save comprehensive output to file if requested
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_output.model_dump(), f, indent=2, ensure_ascii=False)
            logger.info(f"\n💾 Comprehensive results saved to: {args.output_file}")
        else:
            # Default output file with timestamp
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_output_file = f"intersection_analysis_{timestamp_str}.json"
            with open(default_output_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_output.model_dump(), f, indent=2, ensure_ascii=False)
            logger.info(f"\n💾 Comprehensive results saved to: {default_output_file}")
        
    except Exception as e:
        logger.error(f"Error during intersection calculation: {e}")

if __name__ == "__main__":
    main()
