"""
A/B Testing Framework for Messaging Variants
Tests different messaging approaches across platforms
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime
from typing import Dict, List


class MessageTester:
    """A/B testing framework for viral messaging"""
    
    def __init__(self):
        """Initialize message tester"""
        self.variants = {
            'technical': "Built a self-aware GitHub repo using LORD × EKF × Copilot",
            'revenue': "This GitHub repo generates $2.8K/month autonomously",
            'speed': "From zero to monetized repo in 24 hours using AI",
            'mystery': "I taught a GitHub repo to evolve itself. Here's how."
        }
        
        self.results_file = 'data/ab_test_results.json'
    
    def get_variant(self, platform: str = 'twitter') -> Dict:
        """Get a message variant for testing"""
        
        # Load current test state
        test_state = self._load_test_state()
        
        # Determine which variant to use
        if not test_state or test_state.get('completed', False):
            # Start new test
            variant_name = random.choice(list(self.variants.keys()))
            
            test_state = {
                'test_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'start_time': datetime.now().isoformat(),
                'platform': platform,
                'variant': variant_name,
                'completed': False
            }
            
            self._save_test_state(test_state)
        
        variant_name = test_state['variant']
        message = self.variants[variant_name]
        
        return {
            'variant': variant_name,
            'message': message,
            'test_id': test_state['test_id']
        }
    
    def record_result(self, test_id: str, metrics: Dict) -> None:
        """Record test results"""
        
        results = self._load_results()
        
        result = {
            'test_id': test_id,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        results.append(result)
        
        self._save_results(results)
        
        print(f"✓ Recorded results for test {test_id}")
    
    def get_winner(self) -> Dict:
        """Determine winning variant based on historical results"""
        
        results = self._load_results()
        
        if not results:
            return {
                'winner': 'technical',  # Default
                'reason': 'No test data available'
            }
        
        # Aggregate results by variant
        variant_stats = {}
        
        for result in results:
            variant = result.get('variant', 'unknown')
            metrics = result.get('metrics', {})
            
            if variant not in variant_stats:
                variant_stats[variant] = {
                    'count': 0,
                    'total_engagement': 0
                }
            
            variant_stats[variant]['count'] += 1
            variant_stats[variant]['total_engagement'] += metrics.get('engagement', 0)
        
        # Calculate averages and find winner
        best_variant = None
        best_avg = 0
        
        for variant, stats in variant_stats.items():
            avg_engagement = stats['total_engagement'] / stats['count']
            
            if avg_engagement > best_avg:
                best_avg = avg_engagement
                best_variant = variant
        
        return {
            'winner': best_variant or 'technical',
            'average_engagement': best_avg,
            'stats': variant_stats
        }
    
    def generate_report(self) -> str:
        """Generate A/B testing report"""
        
        results = self._load_results()
        winner_info = self.get_winner()
        
        report = f"""# A/B Testing Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Winning Variant

**{winner_info['winner']}**: "{self.variants.get(winner_info['winner'], 'Unknown')}"

- Average Engagement: {winner_info.get('average_engagement', 0):.2f}

## All Variants Performance

"""
        
        stats = winner_info.get('stats', {})
        for variant, data in stats.items():
            avg = data['total_engagement'] / data['count']
            report += f"### {variant}\n"
            report += f"- Message: \"{self.variants.get(variant, 'Unknown')}\"\n"
            report += f"- Tests: {data['count']}\n"
            report += f"- Avg Engagement: {avg:.2f}\n\n"
        
        report += f"\n## Total Tests: {len(results)}\n"
        
        return report
    
    def _load_test_state(self) -> Dict:
        """Load current test state"""
        
        state_file = 'data/ab_test_state.json'
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading test state: {e}")
        
        return {}
    
    def _save_test_state(self, state: Dict) -> None:
        """Save test state"""
        
        state_file = 'data/ab_test_state.json'
        
        try:
            os.makedirs(os.path.dirname(state_file), exist_ok=True)
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving test state: {e}")
    
    def _load_results(self) -> List:
        """Load test results"""
        
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading results: {e}")
        
        return []
    
    def _save_results(self, results: List) -> None:
        """Save test results"""
        
        try:
            os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
            
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            print(f"Error saving results: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='A/B testing for messaging')
    parser.add_argument('--get-variant', action='store_true',
                       help='Get a test variant')
    parser.add_argument('--platform', type=str, default='twitter',
                       help='Platform for testing')
    parser.add_argument('--record', type=str,
                       help='Record results for test ID')
    parser.add_argument('--engagement', type=int, default=0,
                       help='Engagement metric to record')
    parser.add_argument('--report', action='store_true',
                       help='Generate testing report')
    parser.add_argument('--winner', action='store_true',
                       help='Show winning variant')
    
    args = parser.parse_args()
    
    tester = MessageTester()
    
    if args.get_variant:
        variant = tester.get_variant(args.platform)
        print(f"\nTest Variant:")
        print(f"  ID: {variant['test_id']}")
        print(f"  Variant: {variant['variant']}")
        print(f"  Message: {variant['message']}")
    
    elif args.record:
        metrics = {'engagement': args.engagement}
        tester.record_result(args.record, metrics)
    
    elif args.winner:
        winner = tester.get_winner()
        print(f"\nWinning Variant: {winner['winner']}")
        print(f"Average Engagement: {winner.get('average_engagement', 0):.2f}")
    
    elif args.report:
        report = tester.generate_report()
        print(report)
        
        # Save to file
        with open('ab_test_report.md', 'w') as f:
            f.write(report)
        print("\n✓ Report saved to ab_test_report.md")
    
    else:
        print("No action specified. Use --get-variant, --record, --winner, or --report")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
