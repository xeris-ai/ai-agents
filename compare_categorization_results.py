#!/usr/bin/env python3
"""
Categorization Results Comparison Script
Compares category_statistics, message_categories, categories_used, and count_other
across all files in the categorizer_reports folder.
"""

import os
import json
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def load_categorization_results():
    """Load all categorization results from categorizer_reports folder."""
    results = []
    reports_dir = Path("categorizer_reports")
    
    if not reports_dir.exists():
        logger.error("categorizer_reports directory not found!")
        return []
    
    json_files = list(reports_dir.glob("*.json"))
    logger.info(f"📁 Found {len(json_files)} result files to analyze")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract key information
            result = {
                'filename': file_path.name,
                'timestamp': data.get('timestamp', 'unknown'),
                'source_file': extract_source_file(file_path.name),
                'content_type': extract_content_type(file_path.name),
                'agent_type': extract_agent_type(file_path.name),
            }
            
            # Extract message categorization data
            if 'message_categorization' in data:
                msg_cat = data['message_categorization']
                result.update({
                    'categories_used': msg_cat.get('categories_used', []),
                    'message_categories': msg_cat.get('message_categories', []),
                    'category_statistics': msg_cat.get('category_statistics', {}),
                    'count_other': msg_cat.get('count_other', 0),
                    'reasoning': msg_cat.get('reasoning', ''),
                })
            
            # Extract analysis summary data
            if 'analysis_summary' in data:
                summary = data['analysis_summary']
                result.update({
                    'total_messages': summary.get('total_messages', 0),
                    'extracted_categories_count': summary.get('extracted_categories_count', 0),
                    'message_categories_count': summary.get('message_categories_count', 0),
                })
            
            results.append(result)
            logger.info(f"Loaded: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
    
    return results

def extract_source_file(filename):
    """Extract source file name from result filename."""
    # Example: categorization_analysis_10_HR_messages_20251015_170500_only_user_content.json
    # Extract: 10_HR_messages
    parts = filename.replace('categorization_analysis_', '').split('_')
    if len(parts) >= 3:
        return '_'.join(parts[:-2])  # Remove timestamp and content type
    return 'unknown'

def extract_content_type(filename):
    """Extract content type (only_user_content or user_and_assistant_content)."""
    if 'only_user_content' in filename:
        return 'only_user_content'
    elif 'user_and_assistant_content' in filename:
        return 'user_and_assistant_content'
    return 'unknown'

def extract_agent_type(filename):
    """Extract agent type (HR or Bank) from filename."""
    if 'HR' in filename or 'hr' in filename.lower():
        return 'HR'
    elif 'bank' in filename.lower():
        return 'Bank'
    return 'Unknown'

def create_comparison_dataframe(results):
    """Create a pandas DataFrame for easy comparison."""
    if not results:
        return pd.DataFrame()
    
    # Flatten the data for DataFrame
    flattened_data = []
    
    for result in results:
        row = {
            'filename': result['filename'],
            'source_file': result['source_file'],
            'agent_type': result['agent_type'],
            'content_type': result['content_type'],
            'total_messages': result.get('total_messages', 0),
            'categories_used_count': len(result.get('categories_used', [])),
            'categories_used': ', '.join(result.get('categories_used', [])),
            'message_categories_count': len(result.get('message_categories', [])),
            'message_categories': ', '.join(result.get('message_categories', [])),
            'count_other': result.get('count_other', 0),
            'extracted_categories_count': result.get('extracted_categories_count', 0),
            'message_categories_count': result.get('message_categories_count', 0),
        }
        
        # Add category statistics as separate columns
        category_stats = result.get('category_statistics', {})
        for category, percentage in category_stats.items():
            row[f'stat_{category}'] = percentage
        
        flattened_data.append(row)
    
    return pd.DataFrame(flattened_data)

def generate_comparison_report(df):
    """Generate a comprehensive comparison report."""
    if df.empty:
        logger.error("No data to compare!")
        return
    
    print("\n" + "="*80)
    print("CATEGORIZATION RESULTS COMPARISON REPORT")
    print("="*80)
    
    # Basic statistics
    print(f"\nOVERVIEW:")
    print(f"Total files analyzed: {len(df)}")
    print(f"Agent types: {df['agent_type'].value_counts().to_dict()}")
    print(f"Content types: {df['content_type'].value_counts().to_dict()}")
    
    # Group by source file and content type
    print(f"\nDETAILED COMPARISON BY FILE:")
    print("-" * 80)
    
    for source_file in df['source_file'].unique():
        print(f"\n🔍 {source_file.upper()}:")
        file_data = df[df['source_file'] == source_file]
        
        for _, row in file_data.iterrows():
            print(f"\n  📄 {row['content_type']}:")
            print(f"    Total Messages: {row['total_messages']}")
            print(f"    Categories Used: {row['categories_used']}")
            print(f"    Message Categories: {row['message_categories']}")
            print(f"    Count Other: {row['count_other']}")
            
            # Show category statistics
            stat_cols = [col for col in df.columns if col.startswith('stat_')]
            if stat_cols:
                print(f"    Category Statistics:")
                for col in stat_cols:
                    category = col.replace('stat_', '')
                    percentage = row[col]
                    if pd.notna(percentage) and percentage > 0:
                        print(f"      {category}: {percentage}%")
    
    # Comparison between only_user_content vs user_and_assistant_content
    print(f"\n🔄 COMPARISON: ONLY USER vs USER+ASSISTANT:")
    print("-" * 80)
    
    for source_file in df['source_file'].unique():
        file_data = df[df['source_file'] == source_file]
        if len(file_data) == 2:  # Both content types available
            user_only = file_data[file_data['content_type'] == 'only_user_content'].iloc[0]
            user_assistant = file_data[file_data['content_type'] == 'user_and_assistant_content'].iloc[0]
            
            print(f"\n{source_file}:")
            print(f"  Only User Content:")
            print(f"    Categories Used: {user_only['categories_used']}")
            print(f"    Message Categories: {user_only['message_categories']}")
            print(f"    Count Other: {user_only['count_other']}")
            
            print(f"  User + Assistant Content:")
            print(f"    Categories Used: {user_assistant['categories_used']}")
            print(f"    Message Categories: {user_assistant['message_categories']}")
            print(f"    Count Other: {user_assistant['count_other']}")
            
            # Compare count_other
            other_diff = user_assistant['count_other'] - user_only['count_other']
            print(f"  📈 Other Count Difference: {other_diff} ({user_assistant['count_other']} vs {user_only['count_other']})")

def save_detailed_comparison(df):
    """Save detailed comparison to CSV and JSON files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as CSV
    csv_file = f"categorizer_reports/comparison_report_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    logger.info(f"Detailed comparison saved to: {csv_file}")
    
    # Save as JSON
    json_file = f"categorizer_reports/comparison_report_{timestamp}.json"
    df.to_json(json_file, orient='records', indent=2)
    logger.info(f"Detailed comparison saved to: {json_file}")

def main():
    """Main function to run the comparison analysis."""
    logger.info("Starting categorization results comparison...")
    
    # Load all results
    results = load_categorization_results()
    if not results:
        logger.error("No results found to compare!")
        return
    
    # Create comparison DataFrame
    df = create_comparison_dataframe(results)
    if df.empty:
        logger.error("Failed to create comparison data!")
        return
    
    # Generate and display report
    generate_comparison_report(df)
    
    # Save detailed comparison
    save_detailed_comparison(df)
    
    logger.info("✅ Comparison analysis complete!")

if __name__ == "__main__":
    main()
