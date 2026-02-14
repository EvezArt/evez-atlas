"""
Referral Tracker
Tracks traffic sources and top referrers
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List


class ReferralTracker:
    """Tracks and rewards top traffic referrers"""
    
    def __init__(self):
        """Initialize referral tracker"""
        self.github_token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY', 'EvezArt/Evez666')
        self.api_base = 'https://api.github.com'
        self.tracking_file = 'data/referral_history.json'
    
    def log_referrer(self, source: str, visits: int = 1) -> None:
        """Log a referral source"""
        
        history = self._load_history()
        
        # Find or create entry for this source
        found = False
        for entry in history:
            if entry['source'] == source:
                entry['visits'] += visits
                entry['last_seen'] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            history.append({
                'source': source,
                'visits': visits,
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            })
        
        self._save_history(history)
        
        print(f"✓ Logged {visits} visit(s) from {source}")
    
    def get_top_referrers(self, limit: int = 10) -> List[Dict]:
        """Get top referrers by visit count"""
        
        history = self._load_history()
        
        # Sort by visits
        sorted_referrers = sorted(
            history,
            key=lambda x: x['visits'],
            reverse=True
        )
        
        return sorted_referrers[:limit]
    
    def sync_with_github(self) -> None:
        """Sync referral data from GitHub API"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}/traffic/popular/referrers",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                referrers = response.json()
                
                print(f"Found {len(referrers)} referrers from GitHub")
                
                for ref in referrers:
                    source = ref.get('referrer', 'unknown')
                    count = ref.get('count', 0)
                    
                    self.log_referrer(source, count)
                
                print(f"✓ Synced {len(referrers)} referrers")
            
        except Exception as e:
            print(f"Error syncing with GitHub: {e}")
    
    def generate_report(self) -> str:
        """Generate referral tracking report"""
        
        top_referrers = self.get_top_referrers(10)
        
        report = f"""# Referral Tracking Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Top Referrers

"""
        
        if top_referrers:
            for i, ref in enumerate(top_referrers, 1):
                report += f"{i}. **{ref['source']}**\n"
                report += f"   - Visits: {ref['visits']}\n"
                report += f"   - First seen: {ref['first_seen']}\n"
                report += f"   - Last seen: {ref['last_seen']}\n\n"
        else:
            report += "No referral data available.\n"
        
        report += f"\n## Reward Top Referrers\n\n"
        report += "Consider rewarding top referrers with:\n"
        report += "- Free sponsor tier access\n"
        report += "- Premium product discounts\n"
        report += "- Recognition in README\n"
        report += "- Special contributor badge\n"
        
        return report
    
    def _load_history(self) -> List:
        """Load referral history"""
        
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        
        return []
    
    def _save_history(self, history: List) -> None:
        """Save referral history"""
        
        try:
            os.makedirs(os.path.dirname(self.tracking_file), exist_ok=True)
            
            with open(self.tracking_file, 'w') as f:
                json.dump(history, f, indent=2)
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
    
    tracker = ReferralTracker()
    
    # Sync with GitHub
    tracker.sync_with_github()
    
    # Generate report
    report = tracker.generate_report()
    print("\n" + report)
    
    # Save report
    with open('referral_report.md', 'w') as f:
        f.write(report)
    
    print("\n✓ Report saved to referral_report.md")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
