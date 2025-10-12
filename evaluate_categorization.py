#!/usr/bin/env python3
"""
Improved Agent Categorization Evaluation System
Tests categorization accuracy with better category mapping and expanded category set
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add the parent directory to path to import our agents
sys.path.insert(0, str(Path(__file__).parent))

from agent_categorizer import AgentCategorizer
from agents import list_agents, get_agent


class AgentCategorizationEvaluator:
    """Evaluator with intelligent category mapping"""
    
    def __init__(self):
        self.categorizer = AgentCategorizer()
        
        # Expand the category list with all the categories found in agents
        self._expand_categories()
        
        # Category mapping for better matching
        self.category_mapping = {
            # HR related
            "human resources": ["hr", "human resources", "employee assistant", "people management"],
            "hr": ["hr", "human resources", "employee assistant", "people management"],
            "employee assistant": ["hr", "human resources", "employee assistant", "people management"],
            
            # Financial related
            "financial advisor": ["finance", "financial advisor", "investment", "financial services"],
            "bank advisor": ["bank advisor", "banking", "financial services"],
            "banking": ["bank advisor", "banking", "financial services"],
            "finance": ["finance", "financial advisor", "investment", "financial services"],
            
            # Support related
            "customer support": ["customer support", "assistant", "service"],
            "technical support": ["technical support", "it support", "troubleshooting"],
            "it support": ["technical support", "it support", "troubleshooting"],
            "troubleshooting": ["technical support", "it support", "troubleshooting"],
            
            # Development related
            "devops": ["devops", "infrastructure", "automation", "deployment"],
            "infrastructure": ["devops", "infrastructure", "automation", "deployment"],
            "code review": ["code review", "quality assurance", "software development"],
            "quality assurance": ["code review", "quality assurance", "software development"],
            "software development": ["code review", "quality assurance", "software development"],
            
            # Content related
            "content processing": ["content creation", "summarization", "content processing"],
            "summarization": ["content creation", "summarization", "content processing"],
            "content creation": ["content creation", "summarization", "content processing"],
            
            # Travel related
            "travel planner": ["travel planning", "tourism", "trip planning"],
            "travel planning": ["travel planning", "tourism", "trip planning"],
            "tourism": ["travel planning", "tourism", "trip planning"],
            "trip planning": ["travel planning", "tourism", "trip planning"],
            
            # E-commerce related
            "shopping assistant": ["e-commerce", "retail", "shopping assistant"],
            "e-commerce": ["e-commerce", "retail", "shopping assistant"],
            "retail": ["e-commerce", "retail", "shopping assistant"],
            
            # Healthcare related
            "medical assistant": ["healthcare", "medical assistant", "appointment scheduling"],
            "appointment scheduling": ["healthcare", "medical assistant", "appointment scheduling"],
            "healthcare": ["healthcare", "medical assistant", "appointment scheduling"],
            
            # General
            "assistant": ["assistant", "chatbot", "conversational ai"],
            "chatbot": ["assistant", "chatbot", "conversational ai"],
            "conversational ai": ["assistant", "chatbot", "conversational ai"],
            "general chatbot": ["assistant", "chatbot", "conversational ai"]
        }
        
        self.evaluation_results = []
        self.overall_stats = {
            "total_agents": 0,
            "correct_categorizations": 0,
            "partial_categorizations": 0,
            "incorrect_categorizations": 0,
            "accuracy_percentage": 0.0
        }
    
    def _expand_categories(self):
        """Expand the categorizer's categories with agent-specific categories found during evaluation"""
        # Get all real categories from agents
        agents_data = self.extract_all_agents_data()
        all_real_categories = set()
        
        for agent_data in agents_data:
            real_categories = agent_data.get('expected_categories', [])
            all_real_categories.update(real_categories)
        
        # Add any new categories that don't exist in the categorizer
        current_categories = set(self.categorizer.get_available_categories())
        new_categories = all_real_categories - current_categories
        
        if new_categories:
            print(f"🔄 Found {len(new_categories)} new categories to add:")
            for cat in sorted(new_categories):
                print(f"   + {cat}")
                self.categorizer.add_new_category(cat)
        else:
            print("✅ All agent categories already exist in categorizer")
    
    def extract_all_agents_data(self) -> List[Dict[str, Any]]:
        """Extract all agents data from the agents folder"""
        agents_data = []
        
        try:
            agents_info = list_agents()
            
            for agent_key, agent_info in agents_info.items():
                try:
                    agent_module = get_agent(agent_key)
                    
                    # Extract agent data
                    agent_data = {
                        "agent_key": agent_key,
                        "name": agent_module.AGENT_CONFIG.get("name", agent_key),
                        "description": agent_module.AGENT_CONFIG.get("description", ""),
                        "expected_categories": agent_module.AGENT_CONFIG.get("categories", []),
                        "system_prompt": agent_module.SYSTEM_PROMPT,
                        "tools": agent_module.TOOLS if hasattr(agent_module, 'TOOLS') else [],
                        "has_tools": len(agent_module.TOOLS) > 0 if hasattr(agent_module, 'TOOLS') else False
                    }
                    
                    agents_data.append(agent_data)
                    print(f"✅ Extracted: {agent_data['name']}")
                    
                except Exception as e:
                    print(f"❌ Failed to extract {agent_key}: {e}")
                    continue
            
            return agents_data
            
        except Exception as e:
            print(f"❌ Failed to extract agents: {e}")
            return []
    
    def categorize_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize a single agent and return results"""
        try:
            print(f"🔍 Categorizing: {agent_data['name']}")
            
            # Get AI categorization
            analysis = self.categorizer.categorize_agent(agent_data['system_prompt'])
            
            # Format results
            ai_categories = [cat.name for cat in analysis.categories if cat.confidence >= 0.7]
            ai_confidence_scores = {cat.name: cat.confidence for cat in analysis.categories}
            
            result = {
                "agent_key": agent_data['agent_key'],
                "agent_name": agent_data['name'],
                "expected_categories": agent_data['expected_categories'],
                "ai_categories": ai_categories,
                "ai_confidence_scores": ai_confidence_scores,
                "expected_has_tools": agent_data['has_tools'],
                "ai_has_tools": analysis.has_tools,
                "ai_reasoning": analysis.reasoning,
                "system_prompt": agent_data['system_prompt'][:200] + "..." if len(agent_data['system_prompt']) > 200 else agent_data['system_prompt']
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to categorize {agent_data['name']}: {e}")
            return {
                "agent_key": agent_data['agent_key'],
                "agent_name": agent_data['name'],
                "error": str(e)
            }
    
    def map_categories(self, ai_categories: List[str], expected_categories: List[str]) -> Tuple[List[str], float]:
        """Map AI categories to expected categories using semantic matching"""
        mapped_categories = []
        confidence_scores = []
        
        for ai_cat in ai_categories:
            ai_cat_lower = ai_cat.lower()
            
            # Direct match
            if ai_cat_lower in [exp.lower() for exp in expected_categories]:
                mapped_categories.append(ai_cat)
                confidence_scores.append(1.0)
                continue
            
            # Check category mapping
            for expected_cat in expected_categories:
                expected_cat_lower = expected_cat.lower()
                
                if expected_cat_lower in self.category_mapping:
                    if ai_cat_lower in self.category_mapping[expected_cat_lower]:
                        mapped_categories.append(expected_cat)
                        confidence_scores.append(0.8)  # High confidence for mapped match
                        break
                elif ai_cat_lower in self.category_mapping:
                    if expected_cat_lower in self.category_mapping[ai_cat_lower]:
                        mapped_categories.append(expected_cat)
                        confidence_scores.append(0.8)
                        break
            
            # Partial string match
            for expected_cat in expected_categories:
                expected_cat_lower = expected_cat.lower()
                if (ai_cat_lower in expected_cat_lower or expected_cat_lower in ai_cat_lower) and expected_cat not in mapped_categories:
                    mapped_categories.append(expected_cat)
                    confidence_scores.append(0.6)  # Medium confidence for partial match
                    break
        
        return mapped_categories, sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    def evaluate_categorization(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the categorization accuracy with improved mapping"""
        if "error" in result:
            return {
                "evaluation": "error",
                "category_accuracy": 0.0,
                "tool_detection_accuracy": 0.0,
                "overall_score": 0.0,
                "details": "Categorization failed"
            }
        
        expected_categories = set(result['expected_categories'])
        ai_categories = result['ai_categories']
        
        # Map AI categories to expected categories
        mapped_categories, mapping_confidence = self.map_categories(ai_categories, list(expected_categories))
        mapped_categories_set = set(mapped_categories)
        
        # Calculate category accuracy with mapping
        if len(expected_categories) == 0:
            category_accuracy = 1.0 if len(mapped_categories_set) == 0 else 0.0
        else:
            # Use Jaccard similarity for category matching
            intersection = expected_categories.intersection(mapped_categories_set)
            union = expected_categories.union(mapped_categories_set)
            category_accuracy = len(intersection) / len(union) if len(union) > 0 else 0.0
        
        # Apply mapping confidence as a multiplier
        category_accuracy *= mapping_confidence
        
        # Calculate tool detection accuracy
        tool_detection_accuracy = 1.0 if result['expected_has_tools'] == result['ai_has_tools'] else 0.0
        
        # Overall score (weighted average)
        overall_score = (category_accuracy * 0.8) + (tool_detection_accuracy * 0.2)
        
        # Determine evaluation level
        if overall_score >= 0.8:
            evaluation = "excellent"
        elif overall_score >= 0.6:
            evaluation = "good"
        elif overall_score >= 0.4:
            evaluation = "partial"
        else:
            evaluation = "poor"
        
        return {
            "evaluation": evaluation,
            "category_accuracy": round(category_accuracy, 3),
            "tool_detection_accuracy": round(tool_detection_accuracy, 3),
            "overall_score": round(overall_score, 3),
            "mapping_confidence": round(mapping_confidence, 3),
            "details": {
                "expected_categories": list(expected_categories),
                "ai_categories": ai_categories,
                "mapped_categories": list(mapped_categories_set),
                "category_match": list(intersection),
                "category_missed": list(expected_categories - mapped_categories_set),
                "category_extra": list(mapped_categories_set - expected_categories),
                "expected_tools": result['expected_has_tools'],
                "ai_tools": result['ai_has_tools']
            }
        }
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run complete evaluation on all agents"""
        print("🚀 Starting Agent Categorization Evaluation")
        print("=" * 60)
        
        # Extract all agents data
        agents_data = self.extract_all_agents_data()
        
        if not agents_data:
            return {"error": "No agents found"}
        
        print(f"\n📊 Found {len(agents_data)} agents to evaluate")
        print("-" * 40)
        
        # Categorize each agent
        results = []
        for agent_data in agents_data:
            result = self.categorize_agent(agent_data)
            evaluation = self.evaluate_categorization(result)
            
            result["evaluation"] = evaluation
            results.append(result)
            
            # Print progress
            print(f"📈 {result['agent_name']:20} | {evaluation['evaluation']:8} | {evaluation['overall_score']:.3f}")
        
        # Calculate overall statistics
        self._calculate_overall_stats(results)
        
        # Create comprehensive report
        report = {
            "metadata": {
                "evaluation_date": datetime.now().isoformat(),
                "total_agents": len(results),
                "categorizer_model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "confidence_threshold": 0.7,
                "intelligent_mapping": True
            },
            "overall_statistics": self.overall_stats,
            "agent_results": results,
            "summary": self._generate_summary(results)
        }
        
        return report
    
    def _calculate_overall_stats(self, results: List[Dict[str, Any]]):
        """Calculate overall evaluation statistics"""
        total = len(results)
        excellent = sum(1 for r in results if r.get('evaluation', {}).get('evaluation') == 'excellent')
        good = sum(1 for r in results if r.get('evaluation', {}).get('evaluation') == 'good')
        partial = sum(1 for r in results if r.get('evaluation', {}).get('evaluation') == 'partial')
        poor = sum(1 for r in results if r.get('evaluation', {}).get('evaluation') == 'poor')
        
        avg_score = sum(r.get('evaluation', {}).get('overall_score', 0) for r in results) / total if total > 0 else 0
        
        self.overall_stats = {
            "total_agents": total,
            "excellent_categorizations": excellent,
            "good_categorizations": good,
            "partial_categorizations": partial,
            "poor_categorizations": poor,
            "average_score": round(avg_score, 3),
            "accuracy_percentage": round((excellent + good) / total * 100, 1) if total > 0 else 0
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate evaluation summary"""
        # Category analysis
        all_expected = set()
        all_ai = set()
        all_mapped = set()
        category_matches = {}
        
        for result in results:
            if "evaluation" not in result:
                continue
                
            expected = set(result['expected_categories'])
            ai = set(result['ai_categories'])
            mapped = set(result['evaluation']['details']['mapped_categories'])
            
            all_expected.update(expected)
            all_ai.update(ai)
            all_mapped.update(mapped)
            
            # Track category performance
            for cat in expected:
                if cat not in category_matches:
                    category_matches[cat] = {"expected": 0, "detected": 0, "mapped": 0}
                category_matches[cat]["expected"] += 1
                if cat in ai:
                    category_matches[cat]["detected"] += 1
                if cat in mapped:
                    category_matches[cat]["mapped"] += 1
        
        # Calculate category precision/recall
        category_stats = {}
        for cat, stats in category_matches.items():
            precision = stats["mapped"] / stats["expected"] if stats["expected"] > 0 else 0
            category_stats[cat] = {
                "expected_count": stats["expected"],
                "detected_count": stats["detected"],
                "mapped_count": stats["mapped"],
                "precision": round(precision, 3)
            }
        
        return {
            "category_coverage": {
                "total_expected_categories": len(all_expected),
                "total_ai_categories": len(all_ai),
                "total_mapped_categories": len(all_mapped),
                "category_overlap": len(all_expected.intersection(all_mapped)),
                "missing_categories": list(all_expected - all_mapped),
                "extra_categories": list(all_mapped - all_expected)
            },
            "category_performance": category_stats,
            "recommendations": self._generate_recommendations(results)
        }
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        # Analyze poor performers
        poor_results = [r for r in results if r.get('evaluation', {}).get('evaluation') == 'poor']
        if poor_results:
            recommendations.append(f"Focus on improving categorization for {len(poor_results)} agents with poor scores")
        
        # Analyze category mismatches
        all_expected = set()
        all_mapped = set()
        for result in results:
            all_expected.update(result.get('expected_categories', []))
            all_mapped.update(result.get('evaluation', {}).get('details', {}).get('mapped_categories', []))
        
        missing = all_expected - all_mapped
        if missing:
            recommendations.append(f"Consider improving mapping for these categories: {', '.join(missing)}")
        
        extra = all_mapped - all_expected
        if extra:
            recommendations.append(f"Review these extra mapped categories: {', '.join(extra)}")
        
        # Tool detection analysis
        tool_mismatches = sum(1 for r in results if r.get('expected_has_tools') != r.get('ai_has_tools'))
        if tool_mismatches > 0:
            recommendations.append(f"Improve tool detection accuracy ({tool_mismatches} mismatches)")
        
        return recommendations
    
    def save_category_comparison(self, report: Dict[str, Any], filename: str = None):
        """Save detailed category comparison (LLM vs Real) to text file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"category_comparison_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("AGENT CATEGORY COMPARISON REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Agents: {report['metadata']['total_agents']}\n")
                f.write(f"Model: {report['metadata']['categorizer_model']}\n")
                f.write("=" * 50 + "\n\n")
                
                for agent_result in report['agent_results']:
                    agent_name = agent_result['agent_name']
                    real_categories = agent_result['expected_categories']
                    ai_categories = agent_result['ai_categories']
                    evaluation = agent_result['evaluation']
                    
                    f.write(f"AGENT: {agent_name}\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Real Categories:     {', '.join(real_categories)}\n")
                    f.write(f"AI Detected:         {', '.join([cat['name'] for cat in ai_categories])}\n")
                    f.write(f"Evaluation:          {evaluation['evaluation']}\n")
                    f.write(f"Overall Score:        {evaluation['overall_score']:.3f}\n")
                    
                    # Show confidence scores
                    if ai_categories:
                        f.write(f"Confidence Scores:   ")
                        conf_scores = [f"{cat['name']}({cat['confidence']:.2f})" for cat in ai_categories]
                        f.write(", ".join(conf_scores) + "\n")
                    
                    # Show detailed breakdown
                    f.write(f"Category Match:       {evaluation['category_match']:.3f}\n")
                    f.write(f"Tool Detection:       {evaluation['tool_detection']:.3f}\n")
                    f.write(f"Reasoning Quality:    {evaluation['reasoning_quality']:.3f}\n")
                    
                    f.write("\n")
                
                # Add summary statistics
                stats = report['overall_statistics']
                f.write("SUMMARY STATISTICS\n")
                f.write("=" * 20 + "\n")
                f.write(f"Average Score:        {stats['average_score']:.3f}\n")
                f.write(f"Accuracy Rate:        {stats['accuracy_percentage']:.1f}%\n")
                f.write(f"Perfect Matches:      {stats['perfect_matches']}\n")
                f.write(f"Good Matches:         {stats['good_matches']}\n")
                f.write(f"Poor Matches:         {stats['poor_matches']}\n")
                f.write(f"Tool Accuracy:        {stats['tool_accuracy']:.1f}%\n")
                
            print(f"✅ Category comparison saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to save category comparison: {e}")
            return None
    
    def save_results(self, report: Dict[str, Any], filename: str = None):
        """Save evaluation results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_categorization_evaluation_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Evaluation results saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return None
    
    def print_summary(self, report: Dict[str, Any]):
        """Print evaluation summary"""
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)
        
        stats = report['overall_statistics']
        print(f"Total Agents Evaluated: {stats['total_agents']}")
        print(f"Average Score: {stats['average_score']}")
        print(f"Accuracy Rate: {stats['accuracy_percentage']}%")
        print()
        
        print("📈 Performance Breakdown:")
        print(f"  Excellent: {stats['excellent_categorizations']}")
        print(f"  Good: {stats['good_categorizations']}")
        print(f"  Partial: {stats['partial_categorizations']}")
        print(f"  Poor: {stats['poor_categorizations']}")
        print()
        
        # Show individual results
        print("🔍 Individual Results:")
        print("-" * 50)
        for result in report['agent_results']:
            if 'evaluation' in result:
                eval_data = result['evaluation']
                print(f"{result['agent_name']:25} | {eval_data['evaluation']:8} | {eval_data['overall_score']:.3f} | {eval_data['mapping_confidence']:.3f}")
        
        # Show recommendations
        if report['summary']['recommendations']:
            print("\n💡 Recommendations:")
            print("-" * 20)
            for rec in report['summary']['recommendations']:
                print(f"• {rec}")


def main():
    """Main evaluation function"""
    evaluator = AgentCategorizationEvaluator()
    
    # Run evaluation
    report = evaluator.run_evaluation()
    
    if "error" in report:
        print(f"❌ Evaluation failed: {report['error']}")
        return
    
    # Save results
    filename = evaluator.save_results(report)
    
    # Save category comparison
    comparison_filename = evaluator.save_category_comparison(report)
    
    # Print summary
    evaluator.print_summary(report)
    
    print(f"\n🎉 Evaluation completed!")
    print(f"📊 Results saved to: {filename}")
    print(f"📋 Category comparison saved to: {comparison_filename}")
    print(f"📁 Categories file updated: {evaluator.categorizer.categories_file}")
    print(f"📈 Total categories available: {len(evaluator.categorizer.get_available_categories())}")


if __name__ == "__main__":
    main()
