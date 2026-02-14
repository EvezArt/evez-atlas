"""
Star Appreciation Script
Thanks new stargazers (complementary to GitHub Action)
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict


class StarAppreciation:
    """Handles thanking new stargazers"""
    
    def __init__(self):
        """Initialize star appreciation"""
        self.github_token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY', 'EvezArt/Evez666')
        self.api_base = 'https://api.github.com'
    
    def get_recent_stargazers(self, days: int = 1) -> List[Dict]:
        """Get stargazers from the last N days"""
        
        try:
            # Get all stargazers with timestamps
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}/stargazers",
                headers={
                    **self._get_headers(),
                    'Accept': 'application/vnd.github.star+json'
                }
            )
            
            if response.status_code == 200:
                stargazers = response.json()
                
                # Filter to recent ones
                cutoff = datetime.now() - timedelta(days=days)
                recent = []
                
                for star in stargazers:
                    starred_at = datetime.fromisoformat(
                        star['starred_at'].replace('Z', '+00:00')
                    )
                    
                    if starred_at > cutoff:
                        recent.append({
                            'user': star['user']['login'],
                            'starred_at': star['starred_at']
                        })
                
                print(f"Found {len(recent)} new stars in the last {days} day(s)")
                return recent
            
        except Exception as e:
            print(f"Error getting stargazers: {e}")
        
        return []
    
    def thank_stargazers(self, stargazers: List[Dict]) -> int:
        """Thank each stargazer"""
        
        count = 0
        
        for star in stargazers:
            user = star['user']
            
            print(f"Would thank @{user} for starring!")
            # Note: Actual implementation would create issues via API
            # This is handled by the GitHub Action workflow
            
            count += 1
        
        return count
    
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
    
    appreciation = StarAppreciation()
    
    # Get recent stargazers
    stargazers = appreciation.get_recent_stargazers(days=1)
    
    if stargazers:
        print(f"\nNew stargazers:")
        for star in stargazers:
            print(f"  - @{star['user']} (starred at {star['starred_at']})")
        
        # Thank them
        thanked = appreciation.thank_stargazers(stargazers)
        print(f"\n✓ Processed {thanked} new stars")
    else:
        print("\nNo new stars to process")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
