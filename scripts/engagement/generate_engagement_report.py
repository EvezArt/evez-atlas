"""
Engagement Metrics Dashboard
Generates comprehensive engagement reports
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List


class EngagementMetrics:
    """Tracks and reports engagement metrics across platforms"""
    
    def __init__(self):
        """Initialize metrics tracker"""
        self.github_token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY', 'EvezArt/Evez666')
        self.api_base = 'https://api.github.com'
    
    def generate_weekly_report(self) -> Dict:
        """Generate comprehensive weekly engagement report"""
        
        print("Generating weekly engagement report...")
        
        metrics = {
            'github': self._collect_github_metrics(),
            'social': self._collect_social_metrics(),
            'revenue': self._collect_revenue_metrics(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to file
        report_file = f'engagement_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"✓ Report saved to {report_file}")
        
        # Generate markdown summary
        summary = self._generate_markdown_summary(metrics)
        
        summary_file = f'engagement_summary_{datetime.now().strftime("%Y%m%d")}.md'
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"✓ Summary saved to {summary_file}")
        
        return metrics
    
    def _collect_github_metrics(self) -> Dict:
        """Collect GitHub-specific metrics"""
        
        metrics = {
            'stars_gained': self._count_new_stars(),
            'forks': self._count_forks(),
            'traffic_views': self._get_traffic_stats(),
            'referrers': self._top_referrers()
        }
        
        return metrics
    
    def _count_new_stars(self) -> int:
        """Count stars gained in the last week"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                total_stars = data.get('stargazers_count', 0)
                
                print(f"Total stars: {total_stars}")
                
                # Note: To get weekly delta, we'd need to track historical data
                # For now, return total
                return total_stars
            
        except Exception as e:
            print(f"Error counting stars: {e}")
        
        return 0
    
    def _count_forks(self) -> int:
        """Count total forks"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                forks = data.get('forks_count', 0)
                
                print(f"Total forks: {forks}")
                return forks
            
        except Exception as e:
            print(f"Error counting forks: {e}")
        
        return 0
    
    def _get_traffic_stats(self) -> Dict:
        """Get repository traffic statistics"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}/traffic/views",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                views = data.get('count', 0)
                unique = data.get('uniques', 0)
                
                print(f"Traffic - Views: {views}, Unique: {unique}")
                
                return {
                    'views': views,
                    'unique_visitors': unique
                }
            
        except Exception as e:
            print(f"Error getting traffic stats: {e}")
        
        return {'views': 0, 'unique_visitors': 0}
    
    def _top_referrers(self) -> List[Dict]:
        """Get top traffic referrers"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}/traffic/popular/referrers",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                referrers = response.json()
                
                print(f"Top referrers: {len(referrers)}")
                
                return referrers[:5]  # Top 5
            
        except Exception as e:
            print(f"Error getting referrers: {e}")
        
        return []
    
    def _collect_social_metrics(self) -> Dict:
        """Collect social media metrics"""
        
        # Placeholder - would integrate with actual social media APIs
        metrics = {
            'twitter_impressions': 0,
            'reddit_upvotes': 0,
            'hn_points': 0
        }
        
        print("Social metrics: Requires API integration")
        
        return metrics
    
    def _collect_revenue_metrics(self) -> Dict:
        """Collect revenue-related metrics"""
        
        # Placeholder - would integrate with GitHub Sponsors API
        metrics = {
            'new_sponsors': 0,
            'product_sales': 0,
            'monthly_recurring': 0
        }
        
        print("Revenue metrics: Requires Sponsors API integration")
        
        return metrics
    
    def _generate_markdown_summary(self, metrics: Dict) -> str:
        """Generate markdown summary of metrics"""
        
        github = metrics.get('github', {})
        social = metrics.get('social', {})
        revenue = metrics.get('revenue', {})
        
        summary = f"""# Weekly Engagement Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## GitHub Metrics

- **Stars:** {github.get('stars_gained', 0)}
- **Forks:** {github.get('forks', 0)}
- **Traffic Views:** {github.get('traffic_views', {}).get('views', 0)}
- **Unique Visitors:** {github.get('traffic_views', {}).get('unique_visitors', 0)}

### Top Referrers

"""
        
        referrers = github.get('referrers', [])
        if referrers:
            for ref in referrers:
                summary += f"- {ref.get('referrer', 'Unknown')}: {ref.get('count', 0)} visits\n"
        else:
            summary += "- No referrer data available\n"
        
        summary += f"""

## Social Media Metrics

- **Twitter Impressions:** {social.get('twitter_impressions', 0)}
- **Reddit Upvotes:** {social.get('reddit_upvotes', 0)}
- **Hacker News Points:** {social.get('hn_points', 0)}

## Revenue Metrics

- **New Sponsors:** {revenue.get('new_sponsors', 0)}
- **Product Sales:** {revenue.get('product_sales', 0)}
- **Monthly Recurring Revenue:** ${revenue.get('monthly_recurring', 0)}

---

*This report is generated automatically by the Viral Growth Engine*
"""
        
        return summary
    
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
    
    metrics = EngagementMetrics()
    report = metrics.generate_weekly_report()
    
    print("\n" + "="*50)
    print("Engagement Report Generated Successfully")
    print("="*50)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
