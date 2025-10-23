#!/usr/bin/env python3
"""
Batch Categorization Script
Iterates over all message files in messages_data folder and runs categorization
with both user-only and user+assistant content using appropriate system prompts.
"""

import os
import json
import subprocess
import logging
import sys
import importlib.util
from datetime import datetime
from pathlib import Path
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
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Import system prompts from agent files
def load_system_prompts():
    """Load system prompts from agent files using importlib."""
    try:
        # Get the agents directory path
        agents_path = os.path.join(os.path.dirname(__file__), 'agents')
        
        # Load hr_assistant module
        hr_spec = importlib.util.spec_from_file_location(
            "hr_assistant", 
            os.path.join(agents_path, "hr_assistant.py")
        )
        hr_assistant = importlib.util.module_from_spec(hr_spec)
        hr_spec.loader.exec_module(hr_assistant)
        
        # Load bank_advisor module
        bank_spec = importlib.util.spec_from_file_location(
            "bank_advisor", 
            os.path.join(agents_path, "bank_advisor.py")
        )
        bank_advisor = importlib.util.module_from_spec(bank_spec)
        bank_spec.loader.exec_module(bank_advisor)
        
        return hr_assistant.SYSTEM_PROMPT, bank_advisor.SYSTEM_PROMPT
    except Exception as e:
        logger.error(f"Failed to import agent system prompts: {e}")
        logger.error(f"Make sure the agents directory exists and contains hr_assistant.py and bank_advisor.py")
        sys.exit(1)

# Load system prompts
HR_SYSTEM_PROMPT, BANK_SYSTEM_PROMPT = load_system_prompts()

def get_system_prompt_for_file(filename):
    """Determine which system prompt to use based on filename."""
    filename_lower = filename.lower()
    
    if "hr" in filename_lower:
        return HR_SYSTEM_PROMPT
    elif "bank" in filename_lower:
        return BANK_SYSTEM_PROMPT
    else:
        # Default to HR if unclear
        logger.warning(f"Could not determine system prompt for {filename}, using HR default")
        return HR_SYSTEM_PROMPT

def run_categorization(messages_file, system_prompt, content_filter, output_suffix=""):
    """Run categorization for a single configuration."""
    try:
        # Ensure system_prompt is a string
        if isinstance(system_prompt, list):
            system_prompt = ' '.join(str(item) for item in system_prompt)
        
        # Debug logging
        logger.info(f"System prompt type: {type(system_prompt)}")
        logger.info(f"System prompt length: {len(system_prompt) if isinstance(system_prompt, str) else 'N/A'}")
        
        # Build command
        cmd = [
            "python", "agent_categorizer_intersection_categories_prompt.py",
            "--messages-file", messages_file,
            "--system-prompt", system_prompt,
            "--categories", "customer support", "technical support", "sales", "marketing", "finance",
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
        
        # Add content filter argument
        cmd.extend(["--content-filter", content_filter])
        
        # Update output suffix based on content filter
        if content_filter == "user":
            output_suffix += "_user_only"
        elif content_filter == "assistant":
            output_suffix += "_assistant_only"
        else:  # content_filter == "both"
            output_suffix += "_user_and_assistant"
        
        # Create output filename with content type
        messages_filename = Path(messages_file).stem
        output_filename = f"categorizer_reports/categorization_analysis_{messages_filename}{output_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        cmd.extend(["--output-file", output_filename])
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully processed {messages_file} (content_filter={content_filter})")
            return True
        else:
            logger.error(f"❌ Failed to process {messages_file} (content_filter={content_filter})")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception while processing {messages_file}: {e}")
        return False

def main():
    # Ensure categorizer_reports directory exists
    os.makedirs("categorizer_reports", exist_ok=True)
    
    # Get all JSON files in messages_data directory
    messages_data_dir = Path("messages_data")
    if not messages_data_dir.exists():
        logger.error("messages_data directory not found!")
        return
    
    json_files = list(messages_data_dir.glob("*.json"))
    
    for file in json_files:
        logger.info(f"  - {file.name}")
    
    # Process each file
    successful_runs = 0
    total_runs = len(json_files) * 3  # Each file runs three times (user-only, assistant-only, and both)
    
    for json_file in json_files:
        if json_file.name == "50_non_HR_messages.json" or json_file.name == "50_HR_messages.json":
            
            logger.info(f"\n📄 Processing {json_file.name}...")
            
            # Get appropriate system prompt
            system_prompt = get_system_prompt_for_file(json_file.name)
            logger.info(f"Using system prompt for: {'HR' if 'hr' in json_file.name.lower() else 'Bank'}")
            
            # Run with only user content
            # logger.info("🔄 Running with user content only...")
            # if run_categorization(str(json_file), system_prompt, "user", f"_{json_file.stem}"):
            #     successful_runs += 1
            
            # Run with only assistant content
            logger.info("🔄 Running with assistant content only...")
            if run_categorization(str(json_file), system_prompt, "assistant", f"_{json_file.stem}"):
                successful_runs += 1
            
            # # Run with both user and assistant content
            # logger.info("🔄 Running with both user and assistant content...")
            # if run_categorization(str(json_file), system_prompt, "both", f"_{json_file.stem}"):
            #     successful_runs += 1
        
        # Summary
        logger.info(f"\nBatch processing complete!")
        logger.info(f"Successful runs: {successful_runs}/{total_runs}")
        logger.info(f"Failed runs: {total_runs - successful_runs}/{total_runs}")
        
        if successful_runs == total_runs:
            logger.info("🎉 All categorizations completed successfully!")
        else:
            logger.warning("⚠️ Some categorizations failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
