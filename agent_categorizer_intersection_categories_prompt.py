#!/usr/bin/env python3
"""
Agent Categorizer Intersection Categories Prompt System
Extracts categories from agent system prompts and uses them to categorize messages
"""

from typing import List, Dict, Set, Tuple
import dspy
from pydantic import BaseModel, Field
import logging
import argparse
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import the existing agents
from agent_categorizer_messages import MessageCategorizer, MessageAnalysis
from agent_categorizer_prompts import AgentCategorizer, AgentAnalysis

class CategoryExtractionResult(BaseModel):
    """Result of extracting categories from agent system prompt"""
    extracted_categories: List[str] = Field(..., description="Categories extracted from the system prompt")
    system_prompt: str = Field(..., description="The system prompt that was analyzed")
    extraction_reasoning: str = Field(..., description="Explanation of how categories were extracted")

class MessageCategorizationResult(BaseModel):
    """Result of categorizing messages using extracted categories"""
    messages: List[Dict] = Field(..., description="Input messages that were categorized")
    categories_used: List[str] = Field(..., description="Categories that were used for classification")
    message_categories: List[str] = Field(..., description="Categories assigned to the messages")
    category_statistics: Dict[str, float] = Field(..., description="Dictionary mapping ALL categories to their percentage of messages (0.0 to 100.0)")
    reasoning: str = Field(..., description="Explanation of the categorization")
    count_other: int = Field(..., description="Number of messages categorized as other")
class ComprehensiveCategorizationResult(BaseModel):
    """Comprehensive result containing both category extraction and message categorization"""
    timestamp: str = Field(..., description="Analysis timestamp")
    category_extraction: CategoryExtractionResult = Field(..., description="Category extraction result")
    message_categorization: MessageCategorizationResult = Field(..., description="Message categorization result")
    analysis_summary: Dict = Field(..., description="Summary statistics")

class AgentCategorizerIntersectionCategoriesPrompt:
    """Manages category extraction from prompts and message categorization using those categories"""
    
    def __init__(self):
        self.message_agent = MessageCategorizer()
        self.prompt_agent = AgentCategorizer()
    
    def extract_categories_from_prompt(self, system_prompt: str, categories: List[str]) -> CategoryExtractionResult:
        """
        Extract categories from a system prompt using the prompt agent
        
        Args:
            system_prompt: System prompt string to analyze
            
        Returns:
            CategoryExtractionResult with extracted categories
        """
        logger.info("Extracting categories from system prompt...")
        
        # Use the prompt agent to analyze the system prompt

        
        try:
            logger.info(f"Calling prompt_agent.forward with {len(categories)} categories")
            logger.info(f"System prompt length: {len(system_prompt)}")
            
            prompt_results = self.prompt_agent.forward(
                system_prompt=[system_prompt],
                existing_categories=categories
            )
            prompt_analysis = prompt_results[0] if prompt_results else None
            
            if not prompt_analysis:
                raise ValueError("Failed to analyze system prompt")
            
            extracted_categories = prompt_analysis.categories
            extraction_reasoning = f"Categories extracted from system prompt analysis: {prompt_analysis.reasoning}"
            
            logger.info(f"Extracted {len(extracted_categories)} categories from system prompt")
            
            return CategoryExtractionResult(
                extracted_categories=extracted_categories,
                system_prompt=system_prompt,
                extraction_reasoning=extraction_reasoning
            )
            
        except Exception as e:
            logger.error(f"Error extracting categories from prompt: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback: return empty categories
            return CategoryExtractionResult(
                extracted_categories=[],
                system_prompt=system_prompt,
                extraction_reasoning=f"Error during extraction: {str(e)}"
            )
    
    def categorize_messages_with_extracted_categories(
        self, 
        messages: List[Dict], 
        extracted_categories: List[str],
        only_user_content: bool = False
    ) -> MessageCategorizationResult:
        """
        Categorize messages using the extracted categories from the system prompt
        
        Args:
            messages: List of message objects with 'role' and 'content' fields
            extracted_categories: Categories extracted from the system prompt
            
        Returns:
            MessageCategorizationResult with categorization details
        """
        logger.info("Categorizing messages using extracted categories...")
        
        # Add 'other' category to the list of available categories
        categories_with_other = extracted_categories + ["other"]
        
        try:
            if only_user_content:
                messages = [m for m in messages if m["role"] == "user"]
            count_other = sum(1 for m in messages if m["role"] == "user" and m.get("category").lower() == "other")


            # Use the message agent to categorize messages
            messages_results = self.message_agent.forward(
                messages=messages,
                existing_categories=categories_with_other
            )
            messages_analysis = messages_results[0] if messages_results else None
            
            if not messages_analysis:
                raise ValueError("Failed to analyze messages")
            
            message_categories = messages_analysis.categories
            category_statistics = getattr(messages_analysis, 'category_statistics', {})
            
            # Get other percentage from category_statistics if available
            
            logger.info(f"Categorized messages with {len(message_categories)} categories")
            logger.info(f"Category statistics: {category_statistics}")
            
            return MessageCategorizationResult(
                messages=messages,
                categories_used=categories_with_other,
                message_categories=message_categories,
                category_statistics=category_statistics,
                reasoning=messages_analysis.reasoning,
                count_other=count_other
            )
            
        except Exception as e:
            logger.error(f"Error categorizing messages: {e}")
            # Fallback: return basic categorization
            # Calculate percentage for error case (all messages are other)
            total_messages = len(messages)
            
            # Create category_statistics for error case
            error_category_statistics = {}
            for category in categories_with_other:
                error_category_statistics[category] = 100.0 if category == "other" else 0.0
            
            return MessageCategorizationResult(
                messages=messages,
                categories_used=categories_with_other,
                message_categories=["other"],
                category_statistics=error_category_statistics,
                reasoning=f"Error during categorization: {str(e)}",
            )
    
    def process_complete_analysis(
        self, 
        messages: List[Dict], 
        system_prompt: str, 
        categories: List[str], 
        only_user_content: bool = False
    ) -> ComprehensiveCategorizationResult:
        """
        Complete analysis: extract categories from prompt and categorize messages
        
        Args:
            messages: List of message objects with 'role' and 'content' fields
            system_prompt: System prompt string to analyze
            
        Returns:
            ComprehensiveCategorizationResult with full analysis
        """
        logger.info("Starting complete categorization analysis...")
        
        # Step 1: Extract categories from system prompt
        category_extraction = self.extract_categories_from_prompt(system_prompt, categories)
        
        # Step 2: Categorize messages using extracted categories
        message_categorization = self.categorize_messages_with_extracted_categories(
            messages, category_extraction.extracted_categories, only_user_content
        )
        
        # Create analysis summary
        analysis_summary = {
            "total_messages": len(messages),
            "extracted_categories_count": len(category_extraction.extracted_categories),
            "message_categories_count": len(message_categorization.message_categories),
            "category_statistics": message_categorization.category_statistics,
        }
        
        timestamp = datetime.now().isoformat()
        
        return ComprehensiveCategorizationResult(
            timestamp=timestamp,
            category_extraction=category_extraction,
            message_categorization=message_categorization,
            analysis_summary=analysis_summary
        )

def main():
    # Configure DSPy
    dspy.configure(
        lm=dspy.LM(model="bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"),
        adapter=dspy.ChatAdapter(use_native_function_calling=True),
        temperature=0.4,
    )
    
    parser = argparse.ArgumentParser(description="Extract categories from agent prompts and categorize messages")
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
        help="System prompt string to analyze for category extraction"
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        help="List of categories to use for classification (defaults to built-in list)."
    )
    parser.add_argument(
        "--output-file",
        help="File to save comprehensive analysis results as JSON"
    )
    
    parser.add_argument(
        "--only-user-content",
        action="store_true",
        help="Only use user content for categorization"
    )
    try:
        args = parser.parse_args()
        
        # Validate that either messages or messages-file is provided
        if not args.messages and not args.messages_file:
            logger.error("Either --messages or --messages-file must be provided")
            return
        
        if args.messages and args.messages_file:
            logger.error("Cannot provide both --messages and --messages-file")
            return
    
    # Parse messages
   
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
    
    # Initialize categorizer
    categorizer = AgentCategorizerIntersectionCategoriesPrompt()
    
    try:
        # Perform complete analysis
        result = categorizer.process_complete_analysis(
            messages=messages,
            system_prompt=args.system_prompt,
            categories=args.categories,
            only_user_content=args.only_user_content
        )

        
        # Save comprehensive output to file if requested
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
            logger.info(f"\n💾 Comprehensive results saved to: {args.output_file}")
        else:
            # Default output file with timestamp and messages file name
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            messages_filename = os.path.splitext(os.path.basename(args.messages_file))[0]
            default_output_file = f"categorizer_reports/categorization_analysis_{messages_filename}_{timestamp_str}.json"
            
            with open(default_output_file, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
            logger.info(f"\n💾 Comprehensive results saved to: {default_output_file}")
        
    except Exception as e:
        logger.error(f"Error during categorization analysis: {e}")

if __name__ == "__main__":
    main()
