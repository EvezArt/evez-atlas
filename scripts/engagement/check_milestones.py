"""
Milestone Checker
Checks for important milestones and triggers celebrations
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Optional


class MilestoneChecker:
    """Checks for repository milestones and triggers celebrations"""
    
    def __init__(self):
        """Initialize milestone checker"""
        self.github_token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY', 'EvezArt/Evez666')
        self.api_base = 'https://api.github.com'
        
        self.milestone_thresholds = {
            'stars': [10, 25, 50, 100, 250, 500, 1000],
            'forks': [5, 10, 25, 50, 100],
            'sponsors': [1, 5, 10, 25, 50],
            'issues': [10, 25, 50, 100],
            'prs': [10, 25, 50, 100]
        }
    
    def check_all_milestones(self) -> Dict:
        """Check all milestone types"""
        
        print(f"Checking milestones for {self.repo}...")
        
        milestones = {
            'stars': self.check_stars(),
            'forks': self.check_forks(),
            'sponsors': self.check_sponsors(),
            'overall': None
        }
        
        # Determine if any milestone was reached
        milestone_reached = any(
            m and m.get('reached') for m in milestones.values() if m
        )
        
        if milestone_reached:
            # Find the most significant milestone
            for key, milestone in milestones.items():
                if milestone and milestone.get('reached'):
                    milestones['overall'] = milestone
                    break
        
        return milestones
    
    def check_stars(self) -> Optional[Dict]:
        """Check star count milestone"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                stars = data.get('stargazers_count', 0)
                
                print(f"Current stars: {stars}")
                
                # Check if we just hit a milestone
                for threshold in self.milestone_thresholds['stars']:
                    if stars == threshold:
                        return {
                            'type': 'stars',
                            'count': stars,
                            'reached': True,
                            'threshold': threshold
                        }
                
                # Check if we're close to a milestone (within 1)
                for threshold in self.milestone_thresholds['stars']:
                    if stars == threshold - 1:
                        print(f"⚠️  One star away from {threshold} milestone!")
                
                return {
                    'type': 'stars',
                    'count': stars,
                    'reached': False
                }
            
        except Exception as e:
            print(f"Error checking stars: {e}")
        
        return None
    
    def check_forks(self) -> Optional[Dict]:
        """Check fork count milestone"""
        
        try:
            response = requests.get(
                f"{self.api_base}/repos/{self.repo}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                forks = data.get('forks_count', 0)
                
                print(f"Current forks: {forks}")
                
                for threshold in self.milestone_thresholds['forks']:
                    if forks == threshold:
                        return {
                            'type': 'forks',
                            'count': forks,
                            'reached': True,
                            'threshold': threshold
                        }
                
                return {
                    'type': 'forks',
                    'count': forks,
                    'reached': False
                }
            
        except Exception as e:
            print(f"Error checking forks: {e}")
        
        return None
    
    def check_sponsors(self) -> Optional[Dict]:
        """Check sponsor count milestone"""
        
        # Note: This would require GraphQL API for accurate sponsor count
        # For now, return a placeholder
        
        print("Sponsor check: Requires GitHub Sponsors GraphQL API")
        
        return {
            'type': 'sponsors',
            'count': 0,
            'reached': False
        }
    
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
    
    checker = MilestoneChecker()
    milestones = checker.check_all_milestones()
    
    # Output for GitHub Actions
    if milestones.get('overall'):
        overall = milestones['overall']
        
        # Set GitHub Actions outputs
        print(f"::set-output name=milestone_reached::true")
        print(f"::set-output name=milestone_type::{overall['type']}")
        print(f"::set-output name=milestone_count::{overall['count']}")
        
        # Also use newer syntax
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"milestone_reached=true\n")
                f.write(f"milestone_type={overall['type']}\n")
                f.write(f"milestone_count={overall['count']}\n")
        
        print(f"\n🎉 Milestone reached: {overall['count']} {overall['type']}!")
    else:
        print(f"::set-output name=milestone_reached::false")
        
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"milestone_reached=false\n")
        
        print("\nNo milestone reached")
    
    # Output summary
    print("\nMilestone Summary:")
    print("==================")
    for key, milestone in milestones.items():
        if milestone and key != 'overall':
            status = "✓ REACHED" if milestone.get('reached') else "○"
            print(f"{status} {key}: {milestone.get('count', 0)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
