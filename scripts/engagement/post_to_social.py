"""
Social Media Auto-Posting Script
Handles automated posting to Twitter/X for milestones and PRs
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Optional

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("Warning: tweepy not installed. Twitter posting disabled.")


class ViralPoster:
    """Handles automated viral content posting to social media"""
    
    def __init__(self):
        """Initialize social media API clients"""
        self.twitter_client = None
        
        if TWITTER_AVAILABLE:
            try:
                self.twitter_client = tweepy.Client(
                    consumer_key=os.getenv('TWITTER_API_KEY'),
                    consumer_secret=os.getenv('TWITTER_API_SECRET'),
                    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
                )
            except Exception as e:
                print(f"Twitter client initialization failed: {e}")
        
        self.triggers = {
            'new_pr': self.announce_pr,
            'milestone': self.celebrate_milestone,
            'sponsor': self.thank_sponsor,
            'update': self.post_update
        }
    
    def announce_pr(self, pr_data: Dict) -> bool:
        """Auto-tweet when Copilot creates interesting PRs"""
        tweet = f"""🤖 GitHub Copilot just opened a PR for {pr_data.get('title', 'a new feature')}

Watching my cognitive engine evolve itself in real-time.

🔗 {pr_data.get('url', 'github.com/EvezArt/Evez666')}
#AI #GitHub #Automation"""
        
        return self._post_tweet(tweet)
    
    def celebrate_milestone(self, milestone: Dict) -> bool:
        """Post when hitting key metrics"""
        milestone_type = milestone.get('type', 'stars')
        count = milestone.get('count', 0)
        
        if milestone_type == 'stars' and count % 10 == 0:
            tweet = f"""🎉 Just hit {count} stars on Evez666!

Building self-aware repos that:
• Monitor their own state
• Predict future needs
• Generate revenue automatically

Interested? 👉 github.com/EvezArt/Evez666
#AI #OpenSource"""
            
            return self._post_tweet(tweet)
        
        elif milestone_type == 'sponsor':
            tweet = f"""💰 Celebrating {count} amazing sponsors!

Your support drives innovation in:
• Autonomous code evolution
• AI-powered repositories
• Self-aware systems

Join them: github.com/sponsors/EvezArt
#OpenSource #Sponsorship"""
            
            return self._post_tweet(tweet)
        
        return False
    
    def thank_sponsor(self, sponsor_data: Dict) -> bool:
        """Thank new sponsors"""
        sponsor_name = sponsor_data.get('login', 'Unknown')
        tier = sponsor_data.get('tier', 'supporter')
        
        tweet = f"""🙏 Huge thanks to @{sponsor_name} for becoming a {tier}!

Your support enables:
✨ Autonomous AI research
🚀 Open source innovation
🔬 Cognitive systems development

github.com/sponsors/EvezArt"""
        
        return self._post_tweet(tweet)
    
    def post_update(self, update_data: Dict) -> bool:
        """Post general updates"""
        message = update_data.get('message', '')
        
        if message:
            return self._post_tweet(message)
        
        return False
    
    def _post_tweet(self, text: str) -> bool:
        """Post a tweet to Twitter/X"""
        if not self.twitter_client:
            print(f"Twitter client not available. Would post: {text}")
            return False
        
        try:
            response = self.twitter_client.create_tweet(text=text)
            print(f"✓ Tweet posted successfully: {response.data['id']}")
            return True
        except Exception as e:
            print(f"✗ Failed to post tweet: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Post to social media')
    parser.add_argument('--milestone', action='store_true', 
                       help='Post milestone celebration')
    parser.add_argument('--pr', action='store_true',
                       help='Announce new PR')
    parser.add_argument('--sponsor', action='store_true',
                       help='Thank new sponsor')
    parser.add_argument('--message', type=str,
                       help='Custom message to post')
    
    args = parser.parse_args()
    
    poster = ViralPoster()
    
    if args.milestone:
        # Get milestone data from environment
        milestone_type = os.getenv('MILESTONE_TYPE', 'stars')
        milestone_count = int(os.getenv('MILESTONE_COUNT', '0'))
        
        milestone_data = {
            'type': milestone_type,
            'count': milestone_count
        }
        
        poster.celebrate_milestone(milestone_data)
    
    elif args.pr:
        pr_data = {
            'title': os.getenv('PR_TITLE', 'updates'),
            'url': os.getenv('PR_URL', 'https://github.com/EvezArt/Evez666')
        }
        
        poster.announce_pr(pr_data)
    
    elif args.sponsor:
        sponsor_data = {
            'login': os.getenv('SPONSOR_LOGIN', 'supporter'),
            'tier': os.getenv('SPONSOR_TIER', 'sponsor')
        }
        
        poster.thank_sponsor(sponsor_data)
    
    elif args.message:
        update_data = {'message': args.message}
        poster.post_update(update_data)
    
    else:
        print("No action specified. Use --milestone, --pr, --sponsor, or --message")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
