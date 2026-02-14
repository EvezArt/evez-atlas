"""
Metrics Updater
Updates engagement metrics and stores historical data
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict


class MetricsUpdater:
    """Updates and stores engagement metrics"""
    
    def __init__(self):
        """Initialize metrics updater"""
        self.github_token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY', 'EvezArt/Evez666')
        self.api_base = 'https://api.github.com'
        self.metrics_file = 'data/metrics_history.json'
    
    def update_metrics(self) -> Dict:
        """Collect and update current metrics"""
        
        print("Updating engagement metrics...")
        
        current_metrics = {
            'timestamp': datetime.now().isoformat(),
            'github': self._get_github_metrics(),
            'engagement': self._calculate_engagement_rate()
        }
        
        # Load historical data
        history = self._load_history()
        
        # Append current metrics
        history.append(current_metrics)
        
        # Keep last 90 days
        if len(history) > 90:
            history = history[-90:]
        
        # Save updated history
        self._save_history(history)
        
        print(f"✓ Metrics updated and saved")
        
        return current_metrics
    
    def _get_github_metrics(self) -> Dict:
        """Get current GitHub metrics"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                metrics = {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'size': data.get('size', 0)
                }
                
                print(f"GitHub metrics: {metrics['stars']} stars, {metrics['forks']} forks")
                
                return metrics
            
        except Exception as e:
            print(f"Error getting GitHub metrics: {e}")
        
        return {}
    
    def _calculate_engagement_rate(self) -> float:
        """Calculate engagement rate"""
        
        # Placeholder calculation
        # Real implementation would compare current vs previous metrics
        
        return 0.0
    
    def _load_history(self) -> list:
        """Load historical metrics"""
        
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        
        return []
    
    def _save_history(self, history: list) -> None:
        """Save metrics history"""
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            
            with open(self.metrics_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            print(f"✓ Saved {len(history)} historical data points")
            
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _get_headers(self) -> Dict:
        """Get API request headers"""
        
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        if self.github_token:
            headers['Authorization'] = f'Bearer {self.github_token}'
        
        return headers


def main():
    """Main entry point"""
    
    updater = MetricsUpdater()
    metrics = updater.update_metrics()
    
    print("\nCurrent Metrics:")
    print("================")
    
    github = metrics.get('github', {})
    print(f"Stars: {github.get('stars', 0)}")
    print(f"Forks: {github.get('forks', 0)}")
    print(f"Watchers: {github.get('watchers', 0)}")
    print(f"Open Issues: {github.get('open_issues', 0)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
